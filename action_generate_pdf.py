import oom_base
import glob
import os

def generate_pdf(**kwargs):
    generate_pdf_force = kwargs.get("generate_pdf_force", False)
    if generate_pdf_force:
        print("launching generate_pdf")
        import glob
        directory_parts = "C:/gh/oomlout_oomp_current_version/parts"
        #get all the files with label in the name and are .svg
        files = glob.glob(f"{directory_parts}/**/label_*.svg", recursive=True)
        #launch this in another process and return to the app
        
        for file in files:
            file_svg = file
            file_pdf = file.replace(".svg", ".pdf")
            #if the pdf doesn't exist or generate_pdf_force is true
            if not os.path.exists(file_pdf):
                print(f"generating {file_pdf}")
                oom_base.convert_svg_to_pdf(file_input=file_svg, file_output=file_pdf)
        print("generate_pdf finished")


if __name__ == "__main__":
    generate_pdf(generate_pdf_force=True)