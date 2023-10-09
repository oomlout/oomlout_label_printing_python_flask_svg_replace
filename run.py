
from flask import Flask, render_template, request
import oomLabel

app = Flask(__name__,static_folder='static')

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        label = request.form['label']
        return label_print(label)
    return render_template('index.html')

def label_print(label):
    oomLabel.printMessageLabel(label)
    label = request.args.get('label')
    return render_template('label_printing.html', label=label)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=1111, debug=True)
