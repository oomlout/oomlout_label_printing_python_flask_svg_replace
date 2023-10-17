
from flask import Flask, render_template, request, send_from_directory
import oomLabel
import yaml
import os

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
    label = ""
    if request.method == 'POST':
        label = request.form['label']
        label_print(label)
        
    entries = []
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
    return render_template('index.html', entries=entries)

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

def label_print(label):
    #launch oomLabel.printMessageLabel(label) in another process to get back to the page faster
    print(f"printing label {label}")
    import multiprocessing
    p = multiprocessing.Process(target=oomLabel.printMessageLabel, args=(label,))
    p.start()

    #oomLabel.printMessageLabel(label)
    label = request.args.get('label')    

if __name__ == '__main__':
    #app.run(host='0.0.0.0', port=1112, debug=True, threaded=True)
    app.run(host='0.0.0.0', port=1112) # faster launch no debug

