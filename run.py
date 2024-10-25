
from flask import Flask, render_template, request, send_from_directory
import oom_base
import yaml
import os
import oomp
import shlex
import re

file_log = "temporary/log.yaml"
#if log file doesn't exist create it
if not os.path.exists(file_log):
    #make directroies
    os.makedirs(os.path.dirname(file_log), exist_ok=True)
    with open(file_log, 'w') as f:
        yaml.dump([""],f)


app = Flask(__name__,static_folder='static')

modes = ["label", "oomp", "oompa"]

@app.route('/', methods=['GET', 'POST'])
def index():
    entries = []    
    label = ""
    kwargs = {}
    if request.method == 'POST':        
        label = request.form['label']
        kwargs["label"] = label
        label_args = process_args(label)
        kwargs["label_args"] = label_args
        label_args_list = copy.deepcopy(label_args)
        for label_args in label_args_list:            
            #get the mode and content
            if len(label_args) > 1:
                mode = label_args[0]
                content = label_args[-1]
            elif len(label_args) == 1:
                mode = "label"
                content = label_args[0]
            else:
                mode = ""
                content = ""
            #arg check
            arg_list = []
            args = {}
            arg_list.append([["-m","-multiple"],"multiple"])
            for arg in arg_list:
                check_values = arg[0]
                for check_value in check_values:
                    if check_value in label_args:
                        args[arg[1]] = label_args[label_args.index(check_value)+1]
                        kwargs[arg[1]] = args[arg[1]]
            kwargs["args"] = args

            kwargs["mode"] = mode
            kwargs["content"] = content

            
            if mode == "label":
                kwargs = label_print(**kwargs)
            elif mode == "oompa":
                kwargs["file_label_end"] = "label_bolt_76_2_mm_50_8_mm.pdf"
                kwargs = label_print_oomp(**kwargs)
            elif mode == "oomp":
                kwargs["file_label_end"] = "label_oomlout_76_2_mm_50_8_mm.pdf"
                kwargs = label_print_oomp(**kwargs)
        
            

        
        #get last five entries from log file
        with open(file_log, 'r') as f:
            data = yaml.load(f, Loader=yaml.FullLoader)
            entries = data
            if entries == None:
                entries = []
        if label != "":
            entries.append(label)
            #dump to yaml
            with open(file_log, 'w') as f:
                yaml.dump(entries, f)
        entries = entries[-5:]    
        # reverse order
        entries.reverse()
        log_maintenance()
        #delay 1 second
        import time
        time.sleep(0.25)
    status = kwargs.get("status", "none")
    return render_template('index.html', entries=entries, status=status, label=label)

def process_args(label):    
    label = expand_square_brackets(label)        
    if not isinstance(label, list):
        label = [label]
    for i in range(len(label)):
        label[i] = shlex.split(label[i])
    return label


def expand_square_brackets(command):
    command_original = command
    pattern = r'\[([^\]]+)\]'
    try:
        matches = re.finditer(pattern, command)
    except TypeError:
        return command
    expanded_commands = []
    for match in reversed(list(matches)):
        elements_str = match.group(1)
        elements = elements_str.split(',')
        replacements = []
        for element in elements:
            if '-' in element:
                start, end = map(int, element.split('-'))
                if start <= end:
                    replacements.extend(str(i) for i in range(start, end + 1))
            else:
                replacements.append(element)
        expanded_commands.extend([f"{command[:match.start()]}{i}{command[match.end():]}" for i in replacements])
    if len(expanded_commands) == 0:
        return command_original
    else:
        return expanded_commands

def label_process(label):
    import re

    return_value = []

    #split out ranges [1-4]
    matches = re.findall(r'(\[.*?\])', label)
    if len(matches) > 0:
        rang = matches[0].replace("[", "").replace("]", "")
        rang = rang.split("-")
        start = rang[0]
        end = rang[1]
        for i in range(int(start), int(end) + 1):
            return_value.append(label.replace(matches[0], str(i)))

    #split for commas
    if "," in label:
        return_value = label.split(",")
    
    
    #if return value is [] return_value [label  
    if len(return_value) == 0:
        return_value = [label]

    return return_value
    

def log_maintenance():    
    #if file_log has more than 105 entries, take the first 100 and save to an incremented log file, then make the main log file the last five
    """
    with open(file_log, 'r') as f:
        entries = [data for data in yaml.load_all(f, Loader=yaml.FullLoader)]
        log_jump = 2
        if len(entries) > log_jump:
            print(f"file_log has {len(entries)} entries, saving to new file")
            with open(file_log, 'w') as f:
                yaml.dump(entries[-5:], f)
            #save the first 100 entries to a new file
            #get the file name from the directory the next one with format log_{number}
            import glob
            files = glob.glob("tmp/log_*.yaml")
            #get the last number
            numbers = [int(file.split("_")[-1].split(".")[0]) for file in files]
            numbers.sort()
            new_number = numbers[-1] + 1
            new_file = f"tmp/log_{new_number}.yaml"
            #add the oldest 100 entries
            with open(new_file, 'w') as f:
                yaml.dump(entries[:log_jump], f)
            #make the new log file the 5 most recent entries
            with open(file_log, 'w') as f:
                yaml.dump(entries[-1:], f)
    """        


#avoid caching
@app.route('/static/<path:filename>')
def serve_static(filename):
    return send_from_directory('static', filename)

import copy

def label_print(**kwargs):
    content = kwargs.get("content", "")
    labels = label_process(content)
    for label in labels:
        kwargs["content"] = label
        p3 = copy.deepcopy(kwargs)
        content = p3['content']
        content = content.replace("!", "\n")   
        p3["content"] = content
        #launch oomLabel.printMessageLabel(label) in another process to get back to the page faster
        print(f"printing label {content}")

        oom_base.print_message_label(**p3)
        pass
    return p3

def label_print_oomp(**kwargs):
    p3 = copy.deepcopy(kwargs)
    content = p3['content']
    #get style it's character 5
    style = p3.get("style", "")
    
    #test full oomp
    content=content.lower()
    part_id = oomp_parts_id.get(content, "")
    if part_id == "":
        #check for md5
        part_id = oomp_parts_md5_6.get(content, "")
    if part_id == "":
        #check for md5
        part_id = oomp_parts_md5_6_alpha.get(content, "")
    if part_id == "":
        #check for md5
        part_id = oomp_parts_oomlout_short_code.get(content, "")
    #check bip_39_2_word_space
    if part_id == "":
        part_id = oomp_parts_bip_39_2_word_no_space.get(content, "")       
    #check bip_39_2_word_underscore
    if part_id == "":
        part_id = oomp_parts_bip_39_2_word_underscore.get(content, "")
    if part_id != "":
        if part_id in oomp_parts:
            part = oomp_parts[part_id]
            #file_label_base = "C:/gh/oomlout_oomp_part_src/parts"            
            file_label_base = "C:/gh/oomlout_oomp_current_version_messy/parts"
            
            
            
            file_label_end = kwargs.get("file_label_end","label_oomlout_76_2_mm_50_8_mm.pdf")
            file_label = f"{file_label_base}/{part['id']}/{file_label_end}"
            file_input = file_label
            p3["file_input"] = file_input
            
            #if file label dosen't exist see if it exists as an svg
            if not os.path.exists(file_label):
                file_label_svg = file_label.replace(".pdf", ".svg")
                if os.path.exists(file_label_svg):
                    status = p3.get("status", "")
                    stat = f"generating from svg"
                    print()
                    status += f"{stat}\n"
                    p3["status"] = status
                    oom_base.convert_svg_to_pdf(file_input = file_label_svg)



            oom_base.print_pdf_adobe(**p3)
            p3["status"] = p3.get("status", "") + f"printing {part_id}\n"
            pass
            p3["content"] = part["id"]
            return p3
    else:
        stat = f"part {content} not found"
        print(stat)
        status = p3.get("status", "")
        p3["status"] = f"{status}{stat}\n"
        p3["content"] = content
        return p3
oomp_parts = {}
oomp_parts_id = {}
oomp_parts_md5_6 = {}
oomp_parts_md5_6_alpha = {}
oomp_parts_oomlout_short_code = {}
oomp_parts_bip_39_2_word_no_space = {}
oomp_parts_bip_39_2_word_underscore = {}



def load_parts(**kwargs):
    load_parts_force = kwargs.get("load_parts_force", False)
    global oomp_parts
    #directory_parts = "C:/gh/oomlout_oomp_current_version/parts"
    directory_parts = "C:\\gh\\oomlout_oomp_part_generation_version_1\\parts"
    #test
    #directory_parts = "C:\\gh\\oomlout_oomp_current_version_fast_test"

    pickle_file = "temporary/parts.pickle"
    if os.path.exists(pickle_file) and not load_parts_force:
        import pickle
        with open(pickle_file, "rb") as infile:
            oomp_parts = pickle.load(infile)
    else:
        #get all files called working.yaml using glob
        print("loading parts from yaml")
        import glob
        files = glob.glob(f"{directory_parts}/**/working.yaml", recursive=True)
        count = 0
        for file in files:
            #load yaml
            with open(file, "r") as infile:
                #print a dot
                count += 1
                part = yaml.load(infile, Loader=yaml.FullLoader)
                if part != None:
                    oomp_parts[part["id"]] = part
            #every 1000 print a dot
            if count % 100 == 0:
                print(".", end="", flush=True)
        #save to pickle
        import pickle
        #make directroies
        os.makedirs(os.path.dirname(pickle_file), exist_ok=True)        
        with open(pickle_file, "wb") as outfile:
            pickle.dump(oomp_parts, outfile)
        #make a dictionary of id's
    print("making indexes")
    for part_id in oomp_parts:        
        oomp_parts_id[part_id] = part_id
        part = oomp_parts[part_id]
        #make a dictionary of md5's
        md5 = part.get("md5_6","")
        oomp_parts_md5_6[md5] = part_id
        #make a dictionary of md5's
        md5 = part.get("md5_6_alpha","")
        oomp_parts_md5_6_alpha[md5] = part_id
        #make a dictionary of short_codes
        short_code = part.get("oomlout_short_code",part.get("short_code",""))
        if short_code != "":
            oomp_parts_oomlout_short_code[short_code] = part_id
            if "hardware" in part_id:
                pass
                #print(f"{short_code} {part_id}")
        
        #make a dictionary of bip_39_2_word_space
        bip_39_2_word_no_space = part.get("bip_39_word_no_space_2","")
        if bip_39_2_word_no_space != "":
            oomp_parts_bip_39_2_word_no_space[bip_39_2_word_no_space] = part_id

        #make a dictionary of bip_39_2_word_underscore
        bip_39_2_word_underscore = part.get("bip_39_word_underscore_2","")
        if bip_39_2_word_underscore != "":
            oomp_parts_bip_39_2_word_underscore[bip_39_2_word_underscore] = part_id


def generate_pdf(**kwargs):
    generate_pdf_force = kwargs.get("generate_pdf_force", False)
    if generate_pdf_force:
        print("launching generate_pdf")
        #launch python action_generate_pdf.py with os.system call don't wait to finish
        import subprocess
        subprocess.Popen(["python", "action_generate_pdf.py"])
        
        
        
    

if __name__ == '__main__':
    #app.run(host='0.0.0.0', port=1112, debug=True, threaded=True)
    kwargs = {}
    kwargs["load_parts_force"] = True
    #kwargs["load_parts_force"] = False

    kwargs["generate_pdf_force"] = False
    #kwargs["generate_pdf_force"] = True
    load_parts(**kwargs)
    generate_pdf(**kwargs)
    app.run(host='0.0.0.0', port=1112) # faster launch no debug
    #oom_base.print_message_label(label = "test")