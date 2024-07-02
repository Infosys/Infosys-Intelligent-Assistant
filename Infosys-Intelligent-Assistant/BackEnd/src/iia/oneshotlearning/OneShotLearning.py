__copyright__ = """Copyright 2022 Infosys Ltd.
Use of this source code is governed by MIT license that can be found in the LICENSE file or at
https://opensource.org/licenses/MIT."""

import configparser
import os
import re
from pathlib import Path

import cv2
import numpy as np
import spacy
from bson import json_util
from flask import request
from spacy.pipeline import EntityRuler
from werkzeug.utils import secure_filename

from iia.persistence.mongodbpersistence import MongoDBPersistence
from iia.restservice import RestService
from iia.searchimage.colordescriptor import ColorDescriptor
from iia.utils.log_helper import get_logger

logging = get_logger(__name__)
app = RestService.getApp()
import shutil
import pytesseract
from flask_cors import cross_origin
from flask import send_file
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')

@app.route("/api/createimagevector/save", methods=['POST'])
def create_ImageVector():
    return OneShotLearning.create_ImageVector()


@app.route("/api/imagedetails/save", methods=['POST'])
def save_ImageDetails():
    return OneShotLearning.save_ImageDetails()

@app.route("/api/imagedetails/save/imagevector", methods=['POST'])
def save_AND_upload():
    return OneShotLearning.save_AND_upload()

@app.route("/api/getAttachmentsData/<incident_number>/<image_name>")
def search_image_tess_oneshot(incident_number, image_name):
    return OneShotLearning.search_image_tess_oneshot(incident_number, image_name)

@app.route("/api/getFilesCount/<incident_number>")
def get_FilesCount(incident_number):
    return OneShotLearning.get_FilesCount(incident_number)

# need to pass image name as well from front end
@app.route("/api/getImageNERData/<incident_number>/<image_name>")
def ner_imageentityRecognistaion(incident_number, image_name):
    return OneShotLearning.ner_imageentityRecognistaion(incident_number, image_name)

@app.route("/api/newimage/savevector", methods=['POST'])
def create_newImageVector_save():
    return OneShotLearning.create_newImageVector_save()

@app.route("/api/saveimageAnalysisColumnNames", methods=['POST'])
def save_ScreenshotAnalysis_Columns():
    return OneShotLearning.save_ScreenshotAnalysis_Columns()

@app.route("/api/imageAnalysis/getColumnNames", methods=['GET'])
def get_imageAnalysisColumnNames():
    return OneShotLearning.get_imageAnalysisColumnNames()

@app.route("/api/bpmnIIAUpload/<camunda_name>", methods=["POST"])
@cross_origin()
def uploadIIADiagram(camunda_name):
    return OneShotLearning.uploadIIADiagram(camunda_name)

@app.route("/api/getImageApplicationFlow", methods=["Get"])
def getApplicationFlow():
    return OneShotLearning.getApplicationFlow()

@app.route("/api/saveApplicationBPMN/<name>", methods=["POST"])
def saveApplicationBPMN(name):
    return OneShotLearning.saveApplicationBPMN(name)

@app.route("/api/editApplicationBPMN/<name>", methods=["GET"])
def editApplicationBPMN(name):
    return OneShotLearning.editApplicationBPMN(name)

@app.route("/api/newApplicationBPMN/<name>", methods=["GET"])
def newApplicationBPMN(name):
    return OneShotLearning.newApplicationBPMN(name)

@app.route("/api/imageAnalysisUsageDoc", methods=["Get"])
def downloadImgAnalysisDoc():
    return OneShotLearning.downloadImgAnalysisDoc()

@app.route("/api/trainedImageData/<applicationName>/<taskName>")
def getTrainedImagesData(applicationName, taskName):
    return OneShotLearning.getTrainedImagesData(applicationName, taskName)

@app.route("/api/get_image/<image_name>/<applicationName>/<taskName>")
def get_image(image_name, applicationName, taskName):
    print("hitting getimage")
    return OneShotLearning.get_image(image_name, applicationName, taskName)

@app.route("/api/DeleteRecord_and_ImageFile/<image_name>/<applicationName>/<taskName>", methods=["Delete"])
def delete_DBrecord_File(image_name, applicationName, taskName):
    print("hit deleting record")
    return OneShotLearning.delete_DBrecord_File(image_name, applicationName, taskName)

class OneShotLearning:

    def __init__(self, params):
        '''
        Constructor
        '''

    @staticmethod
    def allowed_file(filename):
        ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg'])
        return '.' in filename and \
               filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

    @staticmethod
    def save_AND_upload():
        try:
            print("new save upload")
            try:
                file = request.files
                print("STR FILE", str(file))
            except:
                raise Exception('File has not been recieved.')
            if (not file):
                print("No file uploaded. please upload png file.")
                logging.error("%s: No file uploaded. please upload png file." % RestService.timestamp())
                return 'failure'
            else:
                try:
                    # validating the extensions of images 
                    for file_name in file:
                        each_file = file.getlist(file_name)
                        print("h1", each_file)
                        ext = (each_file[0].filename.split("."))[1]
                        if ext.lower() not in ['png', 'jpg', 'jpeg']:
                            print("Supports only png and jpg file format. please upload correct file.")
                            logging.error(
                                "%s: Supports only png and jpg file format. please upload correct file." % RestService.timestamp())
                            return 'failure'
                except Exception as e:
                    print("some exception occured while validating extension of files uploaded")
                    logging.error(
                        "%s:Some exception occured while validating extension of files uploaded." % RestService.timestamp())
                    return 'failure'

            mapping_details = request.form.get('mappedHeaders')
            image_data = json_util.loads(mapping_details)
            print(type(image_data))
        
            for i in range(len(image_data)):
                print("inside", i)
                del image_data[i]['url']  
            print("image_data_details", image_data)
            print("datatype while saving ", type(image_data))
            MongoDBPersistence.oneshot_learning_tbl.insert_many(image_data)

            try:
                cd = ColorDescriptor((8, 12, 3))
                for file_name in file:
                    print("indie file loop")
                    wfName = MongoDBPersistence.oneshot_learning_tbl.find_one({'image_name': file_name},
                                                                              {'_id': 0, 'workflow_name': 1})
                    tName = MongoDBPersistence.oneshot_learning_tbl.find_one({'image_name': file_name},
                                                                             {'_id': 0, 'task_name': 1})
                    print("wfName", wfName)
                    print("tName", tName)
                    workflowName = wfName['workflow_name']
                    taskName = tName['task_name']
                    
                    uploads_dir = os.path.join(str(Path.cwd()) + "\\data\\AttachementAnalysis", workflowName)
                    os.makedirs(uploads_dir, exist_ok=True)
                    print("directry", uploads_dir)
                    uploads_dir_sub = os.path.join(
                        str(Path.cwd()) + "\\data\\AttachementAnalysis" + "\\" + workflowName, taskName)
                    print("directry", uploads_dir_sub)
                    os.makedirs(uploads_dir_sub, exist_ok=True)
                    each_file = file.getlist(file_name)
                    print("each_file", each_file)
                    ext = (each_file[0].filename.split("."))[1]
                    file_name = file_name + "." + ext
                    # some issue in extension --No
                    print("image file name with extension ", file_name)
                    each_file[0].save(os.path.join(uploads_dir_sub, secure_filename(file_name)))
                    file_path = os.path.join(uploads_dir_sub, file_name)
                    print("file path is ", file_path)
                    pytesseract.pytesseract.tesseract_cmd = "C:\\Program Files\\Tesseract-OCR\\tesseract.exe"
                    image_to_text = pytesseract.image_to_string(file_path, lang='eng')
                    query = cv2.imread(file_path)
                    features = cd.describe(query)
                    print("length of features", len(features))
                    features = [float(f) for f in features]
                    file_name_fordb = file_name.split(".")[0]
                    
                    MongoDBPersistence.oneshot_learning_tbl.update({'image_name': file_name_fordb},
                                                                   {"$set": {'image_features': features}})
                    MongoDBPersistence.oneshot_learning_tbl.update({'image_name': file_name_fordb}, {
                        "$set": {'image_features': features, 'image_text': image_to_text}})
                
                resp = 'success'
                return resp
            
            except Exception as e:
                logging.info("%s exception occured while calculating image vectors in one shot learning %s " % (
                    RestService.timestamp(), str(e)))
                return 'failure'

        except Exception as e:
            print("exception occured in save upload")
            return 'failure'

    @staticmethod
    def save_ImageDetails():
        try:
            
            print("inside image details2")
            data = request.form
            data = request.get_json()
            for i in range(len(data)):
                del data[i]['url']  
            print("data is ", data)
            print("datatype while saving ", type(data))
            MongoDBPersistence.oneshot_learning_tbl.insert_many(data)
            return 'success'
        except Exception as e:
            logging.info("%s Exception occured while saving Image details forImage Analysis in Oneshot learning %s" % (
                RestService.timestamp(), str(e)))
            return 'failure'

    @staticmethod
    def create_ImageVector():
        print("inside imagevector code2")
        try:
            file = request.files
            print("STR FILE", str(file))

        except:
            raise Exception('File has not been recieved.')

        if (not file):
            print("No file uploaded. please upload png file.")
            logging.error("%s: No file uploaded. please upload png file." % RestService.timestamp())
            return 'failure'

        else:
            try:
                for file_name in file:
                    each_file = file.getlist(file_name)
                    print("each_file", each_file)
                    ext = (each_file[0].filename.split("."))[1]
                    
                    if ext.lower() not in ['png', 'jpg', 'jpeg']:
                        print("Supports only png and jpg file format. please upload correct file.")
                        logging.error(
                            "%s: Supports only png and jpg file format. please upload correct file." % RestService.timestamp())
                        return 'failure'
            except Exception as e:
                print("some exception occured while validating extension of files uploaded")
                logging.error(
                    "%s:Some exception occured while validating extension of files uploaded." % RestService.timestamp())
                return 'failure'

        try:

            cd = ColorDescriptor((8, 12, 3))
            for file_name in file:
                print("indie file loop")
                wfName = MongoDBPersistence.oneshot_learning_tbl.find_one({'image_name': file_name},
                                                                          {'_id': 0, 'workflow_name': 1})
                tName = MongoDBPersistence.oneshot_learning_tbl.find_one({'image_name': file_name},
                                                                         {'_id': 0, 'task_name': 1})
                print("wfName", wfName)
                print("tName", tName)
                workflowName = wfName['workflow_name']
                taskName = tName['task_name']
                uploads_dir = os.path.join(str(Path.cwd()) + "\\data\\AttachementAnalysis", workflowName)
                os.makedirs(uploads_dir, exist_ok=True)
                print("directry", uploads_dir)
                uploads_dir_sub = os.path.join(str(Path.cwd()) + "\\data\\AttachementAnalysis" + "\\" + workflowName,
                                               taskName)
                print("directry", uploads_dir_sub)
                os.makedirs(uploads_dir_sub, exist_ok=True)
                each_file = file.getlist(file_name)
                print("each_file", each_file)
                ext = (each_file[0].filename.split("."))[1]
                file_name = file_name + "." + ext
                print("image file name with extension ", file_name)
                each_file[0].save(os.path.join(uploads_dir_sub, secure_filename(file_name)))
                file_path = os.path.join(uploads_dir_sub, file_name)

                print("file path is ", file_path)
                query = cv2.imread(file_path)
                features = cd.describe(query)
                print("length of features:", len(features))
                features = [float(f) for f in features]
                file_name_fordb = file_name.split(".")[0]
               
                MongoDBPersistence.oneshot_learning_tbl.update({'image_name': file_name_fordb},
                                                               {"$set": {'image_features': features}})
                
            resp = 'success'
            return resp
            
        except Exception as e:
            logging.info("%s exception occured while calculating image vectors in one shot learning %s " % (
                RestService.timestamp(), str(e)))
            return 'failure'

    @staticmethod
    def text_extract(incident_number, filename):
        try:
            
            file_path = str(
                Path.cwd()) + "\\data\\AttachementAnalysis\\uploads" + "\\" + incident_number + "\\" + filename + ".png"
            
            img = cv2.imread(file_path)
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            img = cv2.resize(gray, (0, 0), fx=2, fy=2, interpolation=cv2.INTER_LANCZOS4)
            img = cv2.GaussianBlur(img, (5, 5), 0)
            pytesseract.pytesseract.tesseract_cmd = "C:\\Program Files\\Tesseract-OCR\\tesseract.exe"
            result = pytesseract.image_to_string(img, lang='eng')
            
            return result
        except Exception as e:
            logging.info(
                "%s exception occured in TextExtraction for the incident NUmber-%s" % (RestService.timestamp(), str(e)))
            return 'failure'

    @staticmethod
    def ner_imageentityRecognistaion(incident_number, image_name):
        
        try:
            
            filename = image_name
            print(" inside ner_imageentityRecognistaion()")
    
            file_path = str(
                Path.cwd()) + "\\data\\AttachementAnalysis\\uploads" + "\\" + incident_number + "\\" + filename + ".png"
           
            img = cv2.imread(file_path)
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            img = cv2.resize(gray, (0, 0), fx=2, fy=2, interpolation=cv2.INTER_LANCZOS4)
            img = cv2.GaussianBlur(img, (5, 5), 0)
            pytesseract.pytesseract.tesseract_cmd = "C:\\Program Files\\Tesseract-OCR\\tesseract.exe"
            image_text = pytesseract.image_to_string(img, lang='eng')
            print("text result extracted in NER image entity  is ", image_text)
        except Exception as e:
            logging.info("%s exception occured in image_entityRecognition for the incident Number-%s" % (
                RestService.timestamp(), str(e)))
            respnse = 'failure'
            return json_util.dumps(respnse)

        entity_dct = {}
        
        try:
            doc_flag = MongoDBPersistence.assign_enable_tbl.find_one({})
        except Exception as e:
            logging.error('assign_enable_tbl : %s' % str(e))
        regex_flag = True if doc_flag['regex_enabled'] == 'true' else False
        db_regex_flag = True if doc_flag['db_enabled'] == 'true' else False
        spacy_regex_flag = True if doc_flag['spacy_enabled'] == 'true' else False

        # spacy_regex_flag
        if spacy_regex_flag:
            print("inside Spacy_regex")
            spacy_corpus_dir = 'models/spacy_corpus'
            spacy_corpus_path = Path(spacy_corpus_dir)
            if (spacy_corpus_path.is_dir()):
                
                nlp = spacy.load(spacy_corpus_dir)
                doc = nlp(image_text)
                for ent in doc.ents:
                    if (ent.label_ in entity_dct.keys()):
                        entity_dct[ent.label_].append(ent.text)
                    else:
                        entity_dct[ent.label_] = [ent.text]
                
            else:
                
                logging.info(
                    '%s: spacy_corpus_path not found ... please train algo, save the choices & try again.' % RestService.timestamp())

        if regex_flag:
            print("inside ner regex..")
            regex_dictionary = {}
            try:
                config = configparser.ConfigParser()
                config["DEFAULT"]['path'] = "config/"
                config.read(config["DEFAULT"]["path"] + "iia.ini")
                entities_list = config["NamedEntitiesRegex"]["Entities"]
                entities_list = entities_list.split(',')
                for entity_type in entities_list:
                    entity_regex = config[entity_type]
                    entity_regex = entity_regex.split(',')
                    regex_dictionary[entity_type] = entity_regex
                
            except Exception as e:
                logging.error("Error occured Image NER: Hint: 'Entities' is not defined in 'config/iia.ini' file.")
                entities_list = ["EMAIL,", "SERVER", "ISSUE", "NUMBER", "APPLICATION", "PLATFORM", "TRANSACTION_CODE",
                                 "TABLE", "LEAVEAPPLICATION", "FINANCE"]
                regex_dictionary = {"EMAIL": ["[\w\.-]+@[\w\.-]+"], "SERVER": ["CMT\w+", "CTM\w+", "SIT:?", "CD1\-?"],
                                    "ISSUE": ["run[a-z\s]+ce"], "NUMBER": [
                        "(\d{3}[-\.\s]??\d{3}[-\.\s]??\d{4}|\(\d{3}\)\s*\d{3}[-\.\s]??\d{4}|\d{3}[-\.\s]??\d{4})"],
                                    "APPLICATION": ["Shar\w+nt"], "PLATFORM": ["Az\w+e"],
                                    "TRANSACTION_CODE": ["T[0-9]{3}"], "TABLE": ["CISF"]}
                logging.info(
                    "%s Taking default as 'entitites_list as [EMAIL, SERVER, ISSUE, NUMBER, APPLICATION, PLATFORM, TRANSACTION_CODE, TABLE,LEAVEAPPLICATION,FINANCE]'.." % RestService.timestamp())
            for entity_name, regex_list in regex_dictionary.items():
                for regex in regex_list:
                    match_list = re.findall(regex, image_text, re.I)
                    
                    if (match_list):
                        if (entity_name in entity_dct.keys()):
                            entity_dct[entity_name].append(match_list)
                        else:
                            entity_dct[entity_name] = match_list

        # below is DB NER
        if db_regex_flag:
            print("inside ner db_regex..")
            nmd_entity_lst = list(
                MongoDBPersistence.image_annotation_tbl.find({}, {'_id': 0, 'entity': 1, 'description': 1}))
            image_text_lower = image_text.lower()
            for nmd_entity_item in nmd_entity_lst:
                for item in nmd_entity_item['description']:

                    if item.lower() in image_text_lower:
                        if (nmd_entity_item['entity'] in entity_dct.keys()):
                            entity_dct[nmd_entity_item['entity']].append(item)
                        else:
                            entity_dct[nmd_entity_item['entity']] = [item]
            
        if (entity_dct):
            
            final_entities = []

            for entity, value in entity_dct.items():
                entities = {}
                entities["Entity"] = entity
                entities["Value"] = value
                final_entities.append(entities)
            print("final total image entities ", final_entities)
            
        else:
            logging.info("%s: Not able to find image Named Entities for the ticket number %s " % (
                RestService.timestamp(), incident_number))
            resp = 'failure'

            return resp

        if (final_entities):
            try:
                config = configparser.ConfigParser()
                config["DEFAULT"]['path'] = "config/"
                config.read(config["DEFAULT"]["path"] + "iia.ini")
                required_entities = config["ModuleConfig"]["required_entities"]
                required_entities_list = required_entities.split(',')
            except:
                logging.error(
                    "%s: Error occured: Hint: 'required_entities' is not defined in 'config/iia.ini' file.")
                required_entities_list = ['NAME', 'NUMBER', 'EMAIL', 'SERVER', 'ISSUE', 'GPE', 'PERSON',
                                          'TRANSACTION_CODE', 'TABLE', 'APPLICATIONS', 'LEAVEAPPLICATION', 'FINANCE']
                logging.info(
                    "%s Taking default as 'required_entities = ['NAME', 'PHONE', 'EMAIL', 'APPLICATIONS', 'TRANSACTION_CODE', 'TABLE','LEAVEAPPLICATION','FINANCE']'.." % RestService.timestamp())
            resp = []
            
            for entity in final_entities:
                
                if (entity['Entity'].upper() in required_entities_list):
                    temp = {}
                    temp['Entity'] = entity['Entity']
                    temp['Value'] = entity['Value']
                    resp.append(temp)
            
        else:
            logging.info("%s: Not able to find image Named Entities for the ticket number %s " % (
                RestService.timestamp(), incident_number))
            resp = 'failure'

        return json_util.dumps(resp)

    @staticmethod
    def nlp_extract(result, inc_num):
        try:
           
            nlp = spacy.load("en_core_web_sm", disable=['parser', 'tagger', 'ner', 'lemmatizer'])
            ruler = EntityRuler(nlp, overwrite_ents=True)
            patterns = list(MongoDBPersistence.db.TblEntityMapper.find({}, {"label": 1, "pattern": 1, "_id": 0}))
            
            ruler.add_patterns(patterns)
            nlp.add_pipe("entity_ruler")
            doc = nlp(result)

            Errorlist = []
            for ent in doc.ents:
                if ent.label_ == "error":
                    Errorlist.append(ent.text)
            dict = {}
            error_found = False
            return_res = True
            res = "Resolution Not Found"

            for i in range(len(Errorlist)):
                
                res = MongoDBPersistence.oneshot_learning_tbl.find_one({'error_details': Errorlist[i]},
                                                                       {'_id': 0, 'image_features': 0, 'task_name': 0})
                
                if (res == None):
                    continue
                
                res["application_name"] = res.pop("workflow_name")
                dict.update({Errorlist[i]: res})
                
                res_data = res
                if (res != None):
                    break

            if (res == None):
                res = "Resolution Not Found"

            if (res == "Resolution Not Found"):
                return_res = False
                res_data = res

            return return_res, res_data
        except Exception as e:
            print("Exception ouccured while performing NLP Extract", e)
            logging.info("%s Exception ouccured while performing NLP Extract with details of %s" % (
                RestService.timestamp(), str(e)))

    # checks both tesract and oneshot learning image analysis
    @staticmethod
    def search_image_tess_oneshot(incident_number, image_name):
        try:

            filename = image_name
            
            text = OneShotLearning.text_extract(incident_number, filename)
            if (text == 'failure'):
                return 'failure'
            out_inc, re_data = OneShotLearning.nlp_extract(text, incident_number)
            
            if (out_inc == True):
                return json_util.dumps(re_data)

            if (out_inc == False):
                print("starting general image to image analysis")
                
                filename = image_name

                file_path = str(
                    Path.cwd()) + "\\data\\AttachementAnalysis\\uploads" + "\\" + incident_number + "\\" + filename + ".png"
                print("filepath in imageanalysis ", file_path)
                # calculating features for the currrent  image
                cd = ColorDescriptor((8, 12, 3))
                query = cv2.imread(file_path)
                features = cd.describe(query)
                print("4", len(features))
                features = [float(f) for f in features]
                print("Incoming image converted!!!")
                
                db_image_features = list(MongoDBPersistence.oneshot_learning_tbl.find({}, {'_id': 0, 'image_text': 1,
                                                                                           'image_features': 1,
                                                                                           'image_name': 1}))
                logging.info(f"db_image_features length:  {len(db_image_features)}")
                
                results = {}
                try:
                    for i in range(len(db_image_features)):
                        try:
                            d = OneShotLearning.chi2_distance(features, db_image_features[i]['image_features'])
                            img_name = db_image_features[i]['image_name']
                            results[img_name] = d
                        except Exception as e:
                            logging.error(e, exc_info=True)
                except Exception as e:
                    print('exception...', str(e))
                    logging.error(e, exc_info=True)
                ########## Extract text from current image and check cosine similarity ##########
                print("Inside Cosine Similarity")
                try:
                    
                    filename = image_name
                    print(" inside ner_imageentityRecognistaion()")
                    file_path = str(
                        Path.cwd()) + "\\data\\AttachementAnalysis\\uploads" + "\\" + incident_number + "\\" + filename + ".png"
                    img = cv2.imread(file_path)
                    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                    img = cv2.resize(gray, (0, 0), fx=2, fy=2, interpolation=cv2.INTER_LANCZOS4)
                    img = cv2.GaussianBlur(img, (5, 5), 0)
                    pytesseract.pytesseract.tesseract_cmd = "C:\\Program Files\\Tesseract-OCR\\tesseract.exe"
                    image_text = pytesseract.image_to_string(img, lang='eng')
                except Exception as e:
                    logging.info("%s exception occured in image_entityRecognition for the incident Number-%s" % (
                        RestService.timestamp(), str(e)))
                    respnse = 'failure'
                    return json_util.dumps(respnse)
                cosine_similarity_list = []
                cosine_results = {}
                try:
                    for i in range(len(db_image_features)):
                        d = OneShotLearning.cosine_similarity(image_text, db_image_features[i]['image_text'])
                        cosine_similarity_list.append(d)
                        img_name = db_image_features[i]['image_name']
                        cosine_results[img_name] = d
                        print("Similar image Cosine Similarity : ", cosine_results)
                except Exception as e:
                    print('exception...', str(e))

                try:
                    for key in results:
                        if key in cosine_results:
                            
                            cosine_results[key] = results[key] * 0.45 + cosine_results[key] * 0.55
                        else:
                            pass
                except:
                    print("Dictionary is Empty")
                print("Weigtage Average : ", cosine_results)
                sorted_results = {k: v for k, v in sorted(cosine_results.items(), key=lambda item: item[1])}
                print("sorted results ", sorted_results)

                for key in sorted_results:
                    print("value here", sorted_results[key])
                    if (sorted_results[key] < 50):
                        
                        result = MongoDBPersistence.oneshot_learning_tbl.find_one({'image_name': key},
                                                                                  {'_id': 0, 'image_features': 0,
                                                                                   'image_text': 0})
                        print("results here", result)
                        result["application_name"] = result.pop("workflow_name")
                       
                        break 

                    else:
                        print("No results")
                        
                        return 'failure'
        except Exception as e:
            print("exception is ", e)
            logging.info(" %s exception occured while searching for an image using one shot learning:%s " % (
                RestService.timestamp(), str(e)))
            return 'failure'
        return json_util.dumps(result)

    @staticmethod
    def cosine_similarity(image_text, db_image_text):
        list1 = []
        list2 = []
        image_text_list = word_tokenize(image_text)
        db_image_text_list = word_tokenize(db_image_text)
        
        sw = stopwords.words('english')
        X_set = {w for w in image_text_list if not w in sw}
        Y_set = {w for w in db_image_text_list if not w in sw}

        rvector = X_set.union(Y_set)
        for w in rvector:
            if w in X_set:
                list1.append(1)  
            else:
                list1.append(0)
            if w in Y_set:
                list2.append(1)
            else:
                list2.append(0)

        c = 0
       
        for i in range(len(rvector)):
            c += list1[i] * list2[i]
        cosine = c / float((sum(list1) * sum(list2)) ** 0.5)
        cosine = cosine * 100
        cosine = 100 - cosine
        cosine = np.round(cosine, 2)
        return cosine

    @staticmethod
    def search_image(incident_number):
        try:
            
            data = MongoDBPersistence.oneshot_learning_tbl.find_one({'incident_number': incident_number},
                                                                    {'_id': 0, 'image_name': 1})
            filename = data['image_name']
            
            cd = ColorDescriptor((8, 12, 3))
            
            file_path = str(Path.cwd()) + "\\data\\AttachementAnalysis\\uploads" + "\\" + filename + ".png"
            query = cv2.imread(file_path)
            
            features = cd.describe(query)
            features = [float(x) for x in features]
            
            db_image_features = list(
                MongoDBPersistence.oneshot_learning_tbl.find({}, {'_id': 0, 'image_features': 1, 'image_name': 1}))

            results = {}
            for i in range(len(db_image_features)):
                d = OneShotLearning.chi2_distance(features, db_image_features[i]['image_features'])
                img_name = db_image_features[i]['image_name']
                results[img_name] = d
            sorted_results = {k: v for k, v in sorted(results.items(), key=lambda item: item[1])}
            for key in sorted_results:
                if (sorted_results[key] < 0.5):
                    
                    result = MongoDBPersistence.oneshot_learning_tbl.find_one({'image_name': key},
                                                                              {'_id': 0, 'app_name': 1,
                                                                               'sub_appname': 1, 'error_details': 1,
                                                                               'resolution_steps': 1})
                    
                    break  

                else:
                    print("No results")
                    
                    return 'failure'

        except Exception as e:
            logging.info("%s exception occured while searching for an image using one shot learning:%s " % (
                RestService.timestamp(), str(e)))
            return 'failure'
        return json_util.dumps(result)

    @staticmethod
    def chi2_distance(histA, histB, eps=1e-10):
        # compute the chi-squared distance
        try:
            
            d = 0.5 * np.sum([((a - b) ** 2) / (a + b + eps) for (a, b) in zip(histA, histB)])
            return d
        except Exception as e:
            print("exception occured while calculating Chi_Square DIstance", e)
            logging.info("%s Exception occured while calculating Chi_Square DIstance in one shot learning:%s " % (
                RestService.timestamp(), str(e)))

    @staticmethod
    def create_newImageVector_save():
        
        rec_data = request.get_json()
        try:
            filename = rec_data['incident_number']
            file_path = str(Path.cwd()) + "\\static\\assets\\uploads" + "\\" + filename + ".png"
            
            cd = ColorDescriptor((8, 12, 3))
            query = cv2.imread(file_path)
            features = cd.describe(query)
            features = [float(f) for f in features]

            
            rec_data['image_features'] = features  # adding image features calculated

            # have to copy image from static assets uploads to attachementAnalysis
            dest_file_path = str(Path.cwd()) + "\\data\\AttachementAnalysis\\uploads\\{}.png".format(
                rec_data['image_name'])
            shutil.copyfile(file_path, dest_file_path)

            MongoDBPersistence.oneshot_learning_tbl.insert(rec_data)
            resp = 'success'
            return resp
            
        except Exception as e:
            print("exception occured in training new image vector  ", e)
            logging.info(
                "%s exception occured while calculating image vectors for a new image in one shot learning " % RestService.timestamp())
            logging.info(
                "%s exception occured while calculating image vectors for a new image in one shot learning with details of %s " % (
                    RestService.timestamp(), str(e)))
            return 'failure'

    @staticmethod
    def save_ScreenshotAnalysis_Columns():
        try:
            
            data = request.get_json()
            
            dict_data = {}
            dict_data['Columns'] = data
           
            existing_colum_data = list(MongoDBPersistence.image_analysis_column_tbl.find({}, {'Columns': 1, '_id': 0}))
            
            if (len(existing_colum_data)):
                MongoDBPersistence.image_analysis_column_tbl.update_one({}, {'$set': {"Columns": dict_data['Columns']}},
                                                                        upsert=False)
            else:
                
                MongoDBPersistence.image_analysis_column_tbl.insert(dict_data)
            resp = 'success'
        except Exception as e:
            print("exception occured while saving column names ")
            resp = 'failure'
        return resp

    @staticmethod
    def get_imageAnalysisColumnNames():
        try:
            
            colum_data = list(MongoDBPersistence.image_analysis_column_tbl.find({}, {'_id': 0}))
            
            return json_util.dumps({'response': colum_data[0]['Columns']})
        except Exception as e:
            return json_util.dumps({'response': 'failure'})

    @staticmethod
    def get_FilesCount(incident_number):
        files = {}
        try:
            
            DIR = str(Path.cwd()) + "\\data\\AttachementAnalysis\\uploads" + "\\" + incident_number
            files_count = len([name for name in os.listdir(DIR) if os.path.isfile(os.path.join(DIR, name))])
            files['count'] = files_count
            files['status'] = 'success'
            
            return json_util.dumps(files)
        except Exception as e:
            
            files['status'] = 'failure'
            print("exception occured while getting count of files ", e)
            logging.error(
                "%s:Folder doesnot exist with this incident number-%s " % (RestService.timestamp(), incident_number))
            return json_util.dumps(files)

    @staticmethod
    def uploadIIADiagram(camunda_name):
        
        try:
            
            name = camunda_name
            data = request.form
            xml = data['xmlData']
            
            xml_lines = xml.split("\n")
            associated_Tasks = ""

            for line in xml_lines:
                if ('bpmn2:task' in line):
                    items = line.split('=')
                    for index in range(len(items)):
                        if (' name' in items[index]):
                            name_index = index + 1
                            index_list = [i.start() for i in re.finditer("\"", items[name_index])]
                            start_index = index_list[0] + 1
                            end_index = index_list[1]
                            task_name = items[name_index][start_index: end_index]
                            
                            associated_Tasks = associated_Tasks + "," + " " + task_name
                            break
            associated_Tasks = associated_Tasks.strip(",")
            
            MongoDBPersistence.image_analysis_application_flow_tbl.update_one({'workflow_name': name}, {
                '$set': {'BPMN_Content': xml, 'associated_tasks': associated_Tasks}}, upsert=True)
            return "success"
        except Exception as e:
            logging.error('%s: Error in uploadIIADiagram: %s' % (RestService.timestamp, str(e)))
            print(e)
        return 'failure'

    @staticmethod
    def getApplicationFlow():
        try:
            
            application_flow = MongoDBPersistence.image_analysis_application_flow_tbl.find({}, {"_id": 0,
                                                                                                'BPMN_Content': 0})
            if (application_flow):
                return json_util.dumps(application_flow)
            else:
                return "No applicationflow"

        except Exception as e:
            logging.error('%s: Error in getApplicationFlow: %s' % (RestService.timestamp, str(e)))

            return "Failure"

    @staticmethod
    def saveApplicationBPMN(name):
        try:
            
            xml = request.values.get('xmlData')
            
            print("in saving here")
            MongoDBPersistence.image_analysis_application_flow_tbl.update_one({'workflow_name': name}, {
                '$set': {'BPMN_Content': xml, 'keyword_mapping': ''}}, upsert=True)
            return "Success"
        except Exception as e:
            print(e)
            logging.error('%s: Error in saveApplicationBPMN: %s' % (RestService.timestamp, str(e)))
            return e

    @staticmethod
    def newApplicationBPMN(name):
        try:
        
            print("new here new ", name)
            xml = MongoDBPersistence.image_analysis_defaultflow_tbl.find_one({'workflow_name': name},
                                                                             {"BPMN_Content": 1, "_id": 0})[
                'BPMN_Content']
            
            return xml
        except Exception as e:
            print(e)
            logging.error('%s: Error in newApplicationBPMN: %s' % (RestService.timestamp, str(e)))
            return e

    @staticmethod
    def editApplicationBPMN(name):
        try:
            
            print("edit here new ", name)
            xml = MongoDBPersistence.image_analysis_application_flow_tbl.find_one({'workflow_name': name},
                                                                                  {"BPMN_Content": 1, "_id": 0})[
                'BPMN_Content']
            
            return xml
        except Exception as e:
            print(e)
            logging.error('%s: Error in editApplicationBPMN: %s' % (RestService.timestamp, str(e)))
            return e

    @staticmethod
    def downloadImgAnalysisDoc():
        try:
           
            return send_file(str(Path.cwd()) + "\\data\\ScreenShotAnalysis_UsageGuide.pdf",
                             attachment_filename='ScreenShotAnalysis_UsageGuide.pdf')
        except Exception as e:
            logging.error('%s: Error in downloadImgAnalysisDoc: %s' % (RestService.timestamp, str(e)))
            return str(e)

    @staticmethod
    def getTrainedImagesData(applicationName, taskName):
        try:
            
            print("getting trained imagesadata for ", applicationName, taskName, sep="___")
            imageData = list(
                MongoDBPersistence.oneshot_learning_tbl.find({'workflow_name': applicationName, 'task_name': taskName},
                                                             {'image_features': 0, '_id': 0}))
            print("imageData here test is", imageData)
            return json_util.dumps(imageData)


        except Exception as e:
            logging.error('%s: Error in getTrainedImagesData: %s' % (RestService.timestamp, str(e)))
            return json_util.dumps({'response': 'failure'})
            

    @staticmethod
    def get_image(image_name, applicationName, taskName):
        try:
            
            print("inside get image", image_name)
            

            img_list = os.listdir(str(Path.cwd()) + "\\data\\AttachementAnalysis\\" + applicationName + "\\" + taskName)
            
            for img in img_list:
                if (image_name in img):
                    image_name = img
                    filename, file_extension = os.path.splitext(image_name)
                    filepath = str(
                        Path.cwd()) + "\\data\\AttachementAnalysis\\" + applicationName + "\\" + taskName + "\\" + image_name
                    print("filepath here get image ", filepath)
                    break
            
            file_extension = '.png'.strip(".")
            
            return send_file(filepath, mimetype='image/' + file_extension)
        except Exception as e:
            logging.error('%s: Error in get_image: %s' % (RestService.timestamp, str(e)))
            return "failure"

    @staticmethod
    def delete_DBrecord_File(image_name, applicationName, taskName):
        try:
            
            MongoDBPersistence.oneshot_learning_tbl.remove({'image_name': image_name})
            img_list = os.listdir(str(Path.cwd()) + "\\data\\AttachementAnalysis\\" + applicationName + "\\" + taskName)
            
            for img in img_list:
                if (image_name in img):
                    image_name_ext = img
                    filename, file_extension = os.path.splitext(image_name)
                    filepath = str(
                        Path.cwd()) + "\\data\\AttachementAnalysis\\" + applicationName + "\\" + taskName + "\\" + image_name_ext
                    os.remove(filepath)
                    break
            return "success"
        except Exception as e:
            logging.error('%s: Error in delete_DBrecord_File: %s' % (RestService.timestamp, str(e)))
            return "failure"

