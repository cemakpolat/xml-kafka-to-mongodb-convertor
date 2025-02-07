import os
import random
import time
import threading
from faker import Faker
from flask import Flask
import xml.etree.ElementTree as ET


app = Flask(__name__)

# Load environment variables
output_folder = os.getenv("OUTPUT_FOLDER", "/data/")  # Default to "../data" if not set
num_files_to_generate = int(os.getenv("NUM_FILES", 3))  # Default to 3 if not set
file_gen_time_interval = int(os.getenv("TIME_INTERVAL_IN_SEC", 10))  # Default to 3 if not set
port = int(os.getenv("PORT", 5000))  # Default to 5000 if not set

is_generating = False
generation_thread = None


fake = Faker()


def generate_complex_fake_xml_content():
    root = ET.Element("root")

    for _ in range(random.randint(1, 5)):
        person = ET.SubElement(root, "person")
        person.set("id", str(random.randint(1000, 9999)))
        
        name = ET.SubElement(person, "name")
        name.text = fake.name()
        
        age = ET.SubElement(person, "age")
        age.text = str(random.randint(20, 60))

        address = ET.SubElement(person, "address")
        street = ET.SubElement(address, "street")
        street.text = fake.street_address()

        city = ET.SubElement(address, "city")
        city.text = fake.city()

        contacts = ET.SubElement(person, "contacts")
        for _ in range(random.randint(1, 3)):
            contact = ET.SubElement(contacts, "contact")
            contact_type = ET.SubElement(contact, "type")
            contact_type.text = random.choice(["phone", "email"])
            contact_value = ET.SubElement(contact, "value")
            contact_value.text = fake.phone_number() if contact_type.text == "phone" else fake.email()

    return ET.ElementTree(root)

def save_xml_to_file(tree, folder, filename):
    if not os.path.exists(folder):
        os.makedirs(folder)
    
    file_path = os.path.join(folder, filename)
    with open(file_path, "wb") as file:
        tree.write(file, encoding="utf-8", xml_declaration=True)

def generate_and_save_complex_fake_xml_files(num_files):
    for i in range(1, num_files + 1):
        timestamp = time.strftime("%Y%m%d%H%M%S")
        filename = f"complex_fake_data_file_{timestamp}_{i}.xml"
        xml_content = generate_complex_fake_xml_content()
        save_xml_to_file(xml_content, output_folder, filename)
        print(f"File '{filename}' generated and saved in '{output_folder}' successfully!")

def xml_generation_task():
    global is_generating
    while is_generating:
        generate_and_save_complex_fake_xml_files(num_files_to_generate)
        time.sleep(file_gen_time_interval)

@app.route('/xmlfile/start', methods=['GET'])
def start_generation():
    global is_generating, generation_thread
    if not is_generating:
        is_generating = True
        generation_thread = threading.Thread(target=xml_generation_task)
        generation_thread.start()
        return "XML file generation started.", 200
    else:
        return "XML file generation is already running.", 400

@app.route('/xmlfile/stop', methods=['GET'])
def stop_generation():
    global is_generating, generation_thread
    if is_generating:
        is_generating = False
        if generation_thread:
            generation_thread.join()
        return "XML file generation stopped.", 200
    else:
        return "XML file generation is not running.", 400

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=port)