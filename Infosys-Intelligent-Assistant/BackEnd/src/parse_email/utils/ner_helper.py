__copyright__ = """Copyright 2022 Infosys Ltd.
Use of this source code is governed by MIT license that can be found in the LICENSE file or at
https://opensource.org/licenses/MIT."""
from pathlib import Path
import cv2
import pytesseract
import spacy
from pymongo import MongoClient
import re
import os, sys
from parse_email.utils.config_helper import get_config
from parse_email.utils.log_helper import get_logger, log_setup

logging = get_logger(__name__)

log_setup("parse_email")


def ner_image_entity_recognistaion(file_path: str):

    try:
        logging.info(" inside ner_imageentityRecognistaion()")

        img = cv2.imread(file_path)

        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        img = cv2.resize(gray, (0, 0), fx=2, fy=2, interpolation=cv2.INTER_LANCZOS4)
        img = cv2.GaussianBlur(img, (5, 5), 0)
        pytesseract.pytesseract.tesseract_cmd = get_config('email')['tesseract_path']
        image_text = pytesseract.image_to_string(img, lang='eng')

        logging.info(f"image_text {image_text}")
        return image_text

    except Exception as e:
        logging.error(f"{e} exception occured in image_entityRecognition")
        respnse = 'failure'
        raise Exception(respnse)


def ner_extract_from_text(image_text: str):
    try:
        entity_dct = {}
        try:
            config_mongodb = get_config('mongodb')
            client = MongoClient(config_mongodb['hostname'], int(config_mongodb['port']))
            db = client[config_mongodb['database']]
            collection = db[config_mongodb['collection_name.assign_enable_tbl']]
            doc_flag = collection.find_one({})
        except Exception as e:
            logging.error('assign_enable_tbl : %s' % str(e))
        regex_flag = True if doc_flag['regex_enabled'] == 'true' else False
        db_regex_flag = True if doc_flag['db_enabled'] == 'true' else False
        spacy_regex_flag = True if doc_flag['spacy_enabled'] == 'true' else False


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
                    "spacy_corpus_path not found ... please train algo, save the choices & try again.")
                nlp = spacy.load('en_core_web_md')
                doc = nlp(image_text)
                for ent in doc.ents:
                    if (ent.label_ in entity_dct.keys()):
                        entity_dct[ent.label_].append(ent.text)
                    else:
                        entity_dct[ent.label_] = [ent.text]

        # regex NER
        if regex_flag:
            print("inside ner regex..")
            regex_dictionary = {}
            try:
                config_ner = get_config('NamedEntitiesRegex')

                entities_list = config_ner["Entities"]
                entities_list = entities_list.split(',')
                for entity_type in entities_list:
                    entity_regex = config_ner[entity_type]
                    entity_regex = entity_regex.split(',')
                    regex_dictionary[entity_type] = entity_regex

            except Exception as e:
                logging.error("Error occured Image NER: Hint: 'Entities' is not defined in 'config/iia.ini' file.")
                entities_list = ["EMAIL,", "SERVER", "ISSUE", "NUMBER", "APPLICATION", "PLATFORM", "TRANSACTION_CODE",
                                 "TABLE", "LEAVEAPPLICATION", "FINANCE"]
                regex_dictionary = {"EMAIL": ["[\w\.-]+@[\w\.-]+"], "SERVER": ["CMT\w+", "CTM\w+", "SIT:?", "CD1\-?"],
                                    "ISSUE": ["run[a-z\s]+ce"], "NUMBER": [
                        "(\d{3}[-\.\s]??\d{3}[-\.\s]??\d{4}|\(\d{3}\)\s*\d{3}[-\.\s]??\d{4}|\d{3}[-\.\s]??\d{4})"],
                                    "APPLICATION": ["Shar\w+nt"], "PLATFORM": ["Az\w+e"], "TRANSACTION_CODE": ["T[0-9]{3}"],
                                    "TABLE": ["CISF"]}
                logging.info(
                    f"{e} Taking default as 'entitites_list as [EMAIL, SERVER, ISSUE, NUMBER, APPLICATION, PLATFORM, TRANSACTION_CODE, TABLE,LEAVEAPPLICATION,FINANCE]'..")
            for entity_name, regex_list in regex_dictionary.items():
                for regex in regex_list:
                    match_list = re.findall(regex, image_text, re.I)
                    if (match_list):
                        if (entity_name in entity_dct.keys()):
                            entity_dct[entity_name].append(match_list)
                        else:
                            entity_dct[entity_name] = match_list

        if db_regex_flag:
            print("inside ner db_regex..")
            try:
                collection_image_annotation_tbl = db[config_mongodb['collection_name.image_annotation_tbl']]
                nmd_entity_lst = list(
                    collection_image_annotation_tbl.find({}, {'_id': 0, 'entity': 1, 'description': 1}))
                image_text_lower = image_text.lower()
                for nmd_entity_item in nmd_entity_lst:
                    for item in nmd_entity_item['description']:
                        if item.lower() in image_text_lower:
                            if (nmd_entity_item['entity'] in entity_dct.keys()):
                                entity_dct[nmd_entity_item['entity']].append(item)
                            else:
                                entity_dct[nmd_entity_item['entity']] = [item]
            except Exception as e:
                logging.error(e)
        final_entities = []
        if (entity_dct):
            for entity, value in entity_dct.items():
                entities = {}
                entities["Entity"] = entity
                entities["Value"] = value
                final_entities.append(entities)
            logging.info(f"final total image entities {final_entities}")
    except Exception as e:
        exc_type, excs_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(exc_type, fname, exc_tb.tb_lineno)
        logging.error(e)
        logging.error(f"{exc_type}  {fname}  {exc_tb.tb_lineno}")
        return []

    return final_entities

