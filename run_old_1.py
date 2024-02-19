
from flask import Flask, render_template, request, send_from_directory
import oom_base
import yaml
import os
import oomp

file_log = "tmp/log.yaml"
#if log file doesn't exist create it
if not os.path.exists(file_log):
    #make directroies
    os.makedirs(os.path.dirname(file_log), exist_ok=True)
    with open(file_log, 'w') as f:
        yaml.dump([""],f)


app = Flask(__name__,static_folder='static')

@app.route('/', methods=['GET', 'POST'])
def index():
    entries = []    
    label = ""
    if request.method == 'POST':
        label = request.form['label']
        labels = label_process(label)
        for label in labels:
            if label.startswith("oomp"):
                label = label_print_oomp(label=label)   
            elif label.startswith("mult"):                    
                label_full = label
                #remove mult
                label = label.replace("mult", "")
                #multiple is the first charachter
                multiple = label[0]
                multiple = int(multiple)
                #remove the multiple from the label
                label = label[1:]
                for i in range(multiple):
                    label_print(label=label)

            else:
                label_print(label=label)

        

            
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
    return render_template('index.html', entries=entries)

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
    p3 = copy.deepcopy(kwargs)
    label = p3['label']
    label = label.replace("!", "\n")   
    p3["label"] = label
    #launch oomLabel.printMessageLabel(label) in another process to get back to the page faster
    print(f"printing label {label}")
    import multiprocessing

    target = oom_base.print_message_label
    
    p = multiprocessing.Process(target=target, kwargs=p3)
    p.start()

def label_print_oomp(**kwargs):
    p3 = copy.deepcopy(kwargs)
    label = p3['label']
    #get style it's character 5
    style = label[4]
    #remove oomp and style
    label = label[5:]
    #
    #test full oomp
    label=label.lower()
    part = oomp.parts.get(label, "")
    if part == "":
        #check for md5
        part = oomp.parts_md5_6.get(label, "")
    if part == "":
        #check for md5
        part = oomp.parts_md5_6_alpha.get(label, "")
    if part == "":
        #check for md5
        part = oomp.parts_md5_5.get(label, "")
    if part == "":
        #check for short_code
        part = oomp.parts_short_code.get(label, "")
    if part != "":
        file_label_base = "C:/gh/oomlout_oomp_part_src/parts"
        file_label_end = f"working/working_label_76_2_mm_50_8_mm.pdf"
        file_label = f"{file_label_base}/{part['id']}/{file_label_end}"
        file_input = file_label
        oom_base.print_pdf(file_input=file_input)
        return f'oomp{style}{part["id"]}'
    else:
        print(f"part {label} not found")
        return label

if __name__ == '__main__':
    #app.run(host='0.0.0.0', port=1112, debug=True, threaded=True)
    oomp.load_parts(from_pickle=True)
    app.run(host='0.0.0.0', port=1112) # faster launch no debug
    #oom_base.print_message_label(label = "test")
