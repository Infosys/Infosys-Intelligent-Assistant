/* Copyright 2022 Infosys Ltd.Use of this source code is governed by MIT license that can be found in the LICENSE file or athttps://opensource.org/licenses/MIT.*/
import { Component, OnInit } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Router } from '@angular/router'
import { controlNameBinding } from '../../../../node_modules/@angular/forms/src/directives/reactive_directives/form_control_name';
@Component({
  selector: 'app-application-level-settings',
  templateUrl: './application-level-settings.component.html',
  styleUrls: ['./application-level-settings.component.css']
})
export class ApplicaitonLevelSettingsComponent implements OnInit {
  switchStatusAssign: boolean;
  switchStatusPredict: boolean;
  switchStatusTValue: boolean;
  switchStatisIopsValue: any;
  tValueEnabled: boolean;
  HinglishStatus: boolean = false;
  tValue: number;
  validTValue: boolean = true;
  alertEnable: boolean;
  alertType: string;
  message: string;
  iconName: string;
  accuracyPercent: number;
  alertEnable2: boolean;
  alertEnable4: boolean;
  validAccuracy: boolean;
  validScript: boolean
  customerID: number = 1;
  itsmStatus: boolean;
  fileServerStatus: boolean;
  sharepointStatus: boolean;
  source: string;
  alertEnable3: boolean;
  alertEnable5: boolean;
  alertEnable6: boolean;
  alertEnable10: boolean;
  alertEnable11: boolean;
  itsmUrl: string;
  sharepointUrl: string;
  filePath: string;
  scriptPercent: number;
  iOpsPath: string;
  iOpsEnabled: boolean;
  datasetID: number;
  TVTempValue: number;
  TVTempField: string;
  predictedFields: any = [];
  sourceChosen: string;
  lastsourceChosen: string;
  validColName: boolean
  filter_columns: any
  selectedCol: string
  NER_regEx_Status: boolean;
  NER_DB_Status: boolean;
  NER_spacy_Status: boolean;
  RTChosenAlgorithm: string;
  msteams_enabled: boolean;
  twilio_enabled: boolean;
  hello1: boolean = true;
  mymode: boolean;
  sms_Status: boolean;
  whatsapp_Status: boolean;
  call_Status: boolean;
  toolName: string = '';
  toolNameOthers: string = '';
  ITSMToolNames: any;
  fileFormat: any;
  urlFormat: any;
  userId: string = '';
  password: string = '';
  teams: any = [];
  showUpload: boolean = false;
  loading: boolean = false;
  noRecords = false;
  customerId: number = 1;
  chosenTeam: string = "";
  hasApplicationDetails: boolean = false;
  app_lst: any = [];
  constructor(private httpClient: HttpClient, private httpService: HttpClient, private router: Router) {
  }
  ngOnInit() {
    this.httpService.get('/api/getDatasetTeamNames/' + this.customerId).subscribe(data => {
      if (data['Teams'].length > 0) {
        this.teams = data['Teams'];
        this.httpService.get('/api/getApplicationTeamNames', { responseType: 'text' }).subscribe(team => {
          if (team != 'no team') {
            this.chosenTeam = team;
            this.httpClient.get('/api/getiOpsValues/' + this.customerId + '/' + this.chosenTeam).subscribe(data => {
              this.switchStatisIopsValue = data['iOpsStatus']
              this.iOpsPath = data['iOpsPath']
              if (this.switchStatisIopsValue == "true") {
                this.iOpsEnabled = true;
                this.switchStatisIopsValue = true
              } else {
                this.switchStatisIopsValue = false
                this.iOpsEnabled = false
              }
            })
            this.getStatus();
          }
        });
      } else {
        console.log('No Dataset found!. Create Dataset to proceed with uploading of assignment details');
      }
    }, err => {
      console.log(err);
      throw '';
    });
    // --Get DatasetID--
    let teamID = localStorage.getItem('TeamID');
    this.httpClient.get('/api/getDatasetID/' + this.customerID + '/' + teamID).subscribe(data => {
      this.datasetID = Number(data);
    });
    this.httpClient.get('/api/getScriptMatchPercent').subscribe(data => {
      this.scriptPercent = data["script_match_percent"]
    })
    // --api call to get default kb source name and url--
    // --assume data getting back from api is data--
    // then, let kbSrcNme = data['DefaultKBSource'], assuming kbSrcNme is Sharepoint
    this.httpClient.get('/api/getITSMTools').subscribe((data) => {
      this.ITSMToolNames = data['ITSMToolNames'];
      this.httpClient.get('/api/getdefaultSourceDetails').subscribe(data => {
        this.lastsourceChosen = data['DefaultKBSource']
        if (this.lastsourceChosen == 'Sharepoint') {
          this.sharepointStatus = true;
          this.sharepointUrl = data['SharepointUrl'];
        }
        else if (this.lastsourceChosen == 'ITSM') {
          this.itsmStatus = true;
          this.itsmUrl = data['ITSMUrl'];
          if (this.ITSMToolNames.includes(data['ITSMUrl'])) {
            this.toolName = data['ITSMUrl'];
          } else {
            this.toolName = 'Others';
            this.toolNameOthers = data['ITSMUrl'];
          }
        }
        else if (this.lastsourceChosen == 'File Server') {
          this.fileServerStatus = true;
          this.filePath = data['FilePath'];
        }
        if (data['Related_Tickets_Algorithm'] != undefined) this.RTChosenAlgorithm = data['Related_Tickets_Algorithm'];
        else this.RTChosenAlgorithm = 'textrank';
      })
    })
    this.colname()
  }
  colname() {
    this.httpClient.get("/api/assignmentmodule").subscribe(data => {
      this.filter_columns = data
    })
  }
  teamchange() {
    this.ngOnInit()
  }
  getStatus() {
    this.getPredictedFieldsList();
    this.httpClient.get("/api/getSwitchStatus/" + this.customerId + '/' + this.chosenTeam).subscribe(data => {
      let statusAssign = data['assignment_enabled'];
      let statusTValue = data['t_value_enabled'];
      let TValueDoc = data['tValue'];
      let hinglishvalue = data['non_english_description_flag']
      this.predictedFields.forEach(field => {
        field['tValue'] = 0;
        TValueDoc.forEach(doc => {
          if (field['predictedField'] == doc['predictedField']) {
            field['tValue'] = doc['tValue'];
          }
        });
      });
      let predictionStatus = data['prediction_enabled']
      if (statusAssign == 'true') { this.switchStatusAssign = true; } else { this.switchStatusAssign = false; }
      if (statusTValue == 'true') { this.switchStatusTValue = true; this.tValueEnabled = true; } else { this.switchStatusTValue = false; }
      if (predictionStatus == 'true') { this.switchStatusPredict = true } else { this.switchStatusPredict = false; }
      if (hinglishvalue == 'true') { this.HinglishStatus = true } else { this.HinglishStatus = false; }
      if (data['regex_enabled'] == 'true') { this.NER_regEx_Status = true; } else { this.NER_regEx_Status = false; }
      if (data['db_enabled'] == 'true') { this.NER_DB_Status = true; } else { this.NER_DB_Status = false; }
      if (data['spacy_enabled'] == 'true') { this.NER_spacy_Status = true; } else { this.NER_spacy_Status = false; }
      if (data['sms_enabled'] == 'true') { this.sms_Status = true; } else { this.sms_Status = false; }
      if (data['whatsapp_enabled'] == 'true') { this.whatsapp_Status = true; } else { this.whatsapp_Status = false; }
      if (data['call_enabled'] == 'true') { this.call_Status = true; } else { this.call_Status = false; }
      if (data['msteams_enabled'] == 'true') { this.mymode = true; } else { this.mymode = false; }
      if (data['twilio_enabled'] == 'true') { this.twilio_enabled = true; } else { this.twilio_enabled = false; }
      this.selectedCol = data['assignment_logic_dependancy_field']
    });
    this.httpClient.get("/api/getMatchPercentage").subscribe(data => {
      this.accuracyPercent = Number(data['accuracy_percent']);
    });
  }
  assignmentEnable() {
    let currentStatus: boolean;
    if (this.switchStatusAssign) {
      currentStatus = false;
    }
    else {
      currentStatus = true;
    }
    this.httpClient.put("/api/assignmentEnableStatus/" + 'assignment_enabled' + '/' + currentStatus + '/' + this.customerId + '/' + this.chosenTeam, null, { responseType: 'text' })
      .subscribe(data => {
        this.router.navigateByUrl('');
      });
  }
  PredictionEnable() {
    let currentStatus: boolean;
    if (this.switchStatusPredict) {
      currentStatus = false;
    }
    else {
      currentStatus = true;
    }
    this.httpClient.put("/api/predictionEnableStatus/" + 'prediction_enabled' + '/' + currentStatus + '/' + this.customerId + "/" + this.chosenTeam, null, { responseType: 'text' })
      .subscribe(data => {
        this.router.navigateByUrl('');
      });
  }
  HinglishEnable() {
    let currentStatus: boolean;
    if (this.HinglishStatus) {
      currentStatus = false;
    }
    else {
      currentStatus = true;
    }
    this.httpClient.put("/api/hinglishEnableStatus/" + 'non_english_description_flag' + '/' + currentStatus + '/' + this.customerId + '/' + this.chosenTeam, null, { responseType: 'text' })
      .subscribe(data => {
        this.router.navigateByUrl('');
      });
  }
  //team change
  teamChange() {
    this.noRecords = false;
    this.showUpload = true;
    this.loading = true;
    this.httpService.get('/api/getApplicationDetails/' + this.customerId + '/' + this.chosenTeam).subscribe(data => {
      this.loading = false;
      if (Object.keys(data).length != 0) {
        this.app_lst = data;
        this.hasApplicationDetails = true;
      } else {
        this.noRecords = true;
        this.hasApplicationDetails = false;
        this.app_lst = [];
      }
    }, err => {
      console.log(err);
      throw '';
    });
  }
  iOpsEnable() {
    if (this.switchStatisIopsValue) {
      this.iOpsEnabled = false
    } else {
      this.iOpsEnabled = true;
    }
    this.httpClient.post('/api/insertIopsStatus/' + this.iOpsEnabled + '/' + this.customerId + '/' + this.chosenTeam, { responseType: 'text' }).subscribe(data => {
    })
  }
  saveIopsValue() {
    var iOpsPathFormat = /^(?:[\w]\:|\\)(\\[a-z_\-\s0-9\.]+)+\.(txt|gif|pdf|doc|docx|xls|xlsx|exe)$/;
    if (this.iOpsPath.trim() == '') {
      alert('Please Enter iOps Home path');
      return;
    }
    if (!iOpsPathFormat.test(String(this.iOpsPath.trim().toLowerCase()))) {
      alert('Please Enter Valid iOps Home path');
      return;
    }
    let formdata = new FormData()
    formdata.append('Path', this.iOpsPath)
    if (this.iOpsPath.length != 0 && this.iOpsEnabled) {
      this.httpClient.post('/api/insertIopsPath', formdata, { responseType: 'text' }).subscribe(data => {
        alert(data)
      })
    }
  }
  validateTValue() {
    this.validTValue = true;
    this.predictedFields.forEach(field => {
      if (field['tValue'] < 0 || field['tValue'] > 1 || field['tValue'] == null) {
        this.validTValue = false;
      }
    });
    if (this.validTValue) {
      this.alertEnable = false;
    } else {
      this.alertType = 'warning';
      this.message = 'Wrong input! Value limit: 0 - 1';
      this.iconName = 'clear';
      this.alertEnable = true;
    }
  }
  saveTValue() {
    this.validateTValue();
    if (this.validTValue) {
      this.httpClient.post("/api/insertTValue" + '/' + this.customerId + '/' + this.chosenTeam, this.predictedFields, { responseType: 'text' })
        .subscribe(data => { console.log('success!') });
      this.alertType = 'success';
      this.message = 'Saved Successfully!';
      this.iconName = 'done';
      this.alertEnable = true;
    }
  }
  tValueEnable() {
    let currentStatus: boolean;
    if (this.switchStatusTValue) {
      currentStatus = false;
      this.tValueEnabled = false;
      this.alertEnable = false;
    }
    else {
      currentStatus = true;
      this.tValueEnabled = true;
    }
    this.httpClient.put("/api/assignmentEnableStatus/" + 't_value_enabled' + '/' + currentStatus + '/' + this.customerId + '/' + this.chosenTeam, null, { responseType: 'text' })
      .subscribe(data => {
      });
  }
  disableAlert() {
    this.alertEnable = false;
  }
  validateAccuracy() {
    if (this.accuracyPercent >= 1 && this.accuracyPercent <= 100) {
      this.validAccuracy = true;
      this.alertEnable2 = false;
    } else {
      this.validAccuracy = false;
      this.alertType = 'warning';
      this.message = 'Wrong input! Allowed value limit: 1 - 100';
      this.iconName = 'clear';
    }
  }
  insertAccuracyValue() {
    if (this.validAccuracy == true) {
      this.httpClient.post("/api/insertAccuracyPercent/" + this.accuracyPercent + "/" + this.customerID, null, { responseType: 'text' })
        .subscribe(data => {
          console.log('success!')
        });
      this.alertType = 'success';
      this.message = 'Saved Successfully!';
      this.iconName = 'done';
      this.alertEnable2 = true;
    } else {
      this.alertEnable2 = true;
    }
  }
  validateScriptPercent() {
    if (this.scriptPercent >= 1 && this.scriptPercent <= 100) {
      this.validScript = true;
      this.alertEnable4 = false;
    } else {
      this.validScript = false;
      this.alertType = 'warning';
      this.message = 'Wrong input! Allowed Integer Limit: 1 - 100';
      this.iconName = 'clear';
    }
  }
  insertScriptPercent() {
    if (this.validScript == true) {
      this.httpClient.post("/api/saveScriptMatchPercent/" + this.scriptPercent, { responseType: 'text' })
        .subscribe(data => {
          console.log('success!')
        });
      this.alertType = 'success';
      this.message = 'Saved Successfully!';
      this.iconName = 'done';
      this.alertEnable4 = true;
    } else {
      // this.alertEnable4 = false;
      this.alertEnable4 = true;
    }
  }
  serviceNow(event) {
    if (event) {
      this.fileServerStatus = false;
      this.sharepointStatus = false;
      this.itsmStatus = true;
      this.sourceChosen = 'ITSM';
    } else {
      this.itsmStatus = false;
    }
    this.alertEnable3 = false;
  }
  fileServer(event) {
    if (event) {
      this.fileServerStatus = true;
      this.sharepointStatus = false;
      this.itsmStatus = false;
      this.sourceChosen = 'File Server';
    } else {
      this.fileServerStatus = false;
      // this.sourceChosen = '';
    }
    this.alertEnable3 = false;
  }
  sharepoint(event) {
    if (event) {
      this.itsmStatus = false;
      this.fileServerStatus = false;
      this.sharepointStatus = true;
      this.sourceChosen = 'Sharepoint';
    } else {
      this.sharepointStatus = false;
    }
    this.alertEnable3 = false;
  }
  validateUrls(event) {
    this.alertEnable3 = false;
    let path = event.target.value.trim();
    if (!(path.length == 0)) {
      this.alertEnable3 = false;
    } else {
      this.alertType = 'warning';
      this.message = 'Please enter a valid URL';
      this.iconName = 'clear';
      this.alertEnable3 = true;
    }
  }
  insertColName() {
    if (this.selectedCol.length != 0 && this.selectedCol) {
      this.httpClient.post("/api/saveColName/" + this.selectedCol + this.customerId + '/' + this.chosenTeam, { responseType: 'text' })
        .subscribe(data => {
          console.log('Success!')
        });
      this.alertType = 'success';
      this.message = 'Saved Successfully!';
      this.alertEnable5 = true;
    } else {
      this.alertType = 'danger';
      this.message = 'Could not save!';
      this.alertEnable5 = true;
    }
  }
  RegEx_NER() {
    this.alertEnable6 = false;
  }
  Database_NER() {
    this.alertEnable6 = false;
  }
  Spacy_NER() {
    this.alertEnable6 = false;
  }
  sms_NER() {
    this.alertEnable10 = false;
  }
  whatsapp_NER() {
    this.alertEnable10 = false;
  }
  call_NER() {
    this.alertEnable10 = false;
  }
  ms_teams_notification_NER() {
    this.alertEnable11 = false;
  }
  msteams_NER() {
  }
  twilio_notification() {
    this.httpClient.put("/api/twilioalert/" + this.twilio_enabled, null, { responseType: 'text' })
      .subscribe(data => {
        if (data == 'Success') {
          this.alertType = 'success';
          this.message = 'Saved Successfully!';
        } else {
          this.alertType = 'danger';
          this.message = 'Could not save!';
        }
      }, err => {
        this.alertType = 'danger';
        this.message = 'Could not save!';
        console.error('Could not save! ' + err);
      });
    this.alertEnable11 = true;
  }
  saveNERConfig() {
    this.httpClient.put("/api/nerEnableStatus/" + this.NER_regEx_Status + "/" + this.NER_DB_Status + "/" + this.NER_spacy_Status + '/' + this.customerId + '/' + this.chosenTeam, null, { responseType: 'text' })
      .subscribe(data => {
        if (data == 'Success') {
          this.alertType = 'success';
          this.message = 'Saved Successfully!';
          console.log('Success!')
        } else {
          this.alertType = 'danger';
          this.message = 'Could not save!';
          console.warn('Could not save! please try again');
        }
      }, err => {
        this.alertType = 'danger';
        this.message = 'Could not save!';
        console.error('Could not save! ' + err);
      });
    this.alertEnable6 = true;
  }
  saveAlertConfig() {
    this.httpClient.put("/api/alertEnableStatus/" + this.sms_Status + "/" + this.whatsapp_Status + "/" + this.call_Status + "/" + this.mymode, null, { responseType: 'text' })
      .subscribe(data => {
        if (data == 'Success') {
          this.alertType = 'success';
          this.message = 'Saved Successfully!';
          console.log('Success!')
        } else {
          this.alertType = 'danger';
          this.message = 'Could not save!';
          console.warn('Could not save! please try again');
        }
      }, err => {
        this.alertType = 'danger';
        this.message = 'Could not save!';
        console.error('Could not save! ' + err);
      });
    this.alertEnable10 = true;
  }
  SaveSourceDetails() {
    var nameFormat = /^[a-zA-Z0-9 _.-]*$/;
    if (this.lastsourceChosen == 'ITSM') {
      if (this.toolName == '') {
        this.alertType = 'warning';
        this.message = 'Please enter the ITSM Tool Name'
        this.iconName = 'clear';
        this.alertEnable3 = true;
        return;
      } else if (this.toolName == 'Others' && this.toolNameOthers.trim() == '') {
        this.alertType = 'warning';
        this.message = 'Please enter the ITSM Tool Name Others'
        this.iconName = 'clear';
        this.alertEnable3 = true;
        return;
      } else if (this.toolName == 'Others' && !nameFormat.test(String(this.toolNameOthers).toLowerCase())) {
        this.alertType = 'warning';
        this.message = 'Please enter the valid ITSM Tool Name Others'
        this.iconName = 'clear';
        this.alertEnable3 = true;
        return;
      } else {
        this.toolName = (this.toolName != "Others" ? this.toolName : this.toolNameOthers);
        this.alertEnable3 = false;
      }
      let json_data2 = {};
      if (this.itsmStatus && this.toolName != '') {
        json_data2['source'] = this.lastsourceChosen;
        json_data2['ITSMUrl'] = this.toolName;
        json_data2['url'] = this.toolName;
        if (!(json_data2['url'].length == 0)) {
          this.httpClient.post("/api/insertITSMSourceDetails", json_data2, { responseType: 'text' })
            .subscribe(data => {
              if (data != 'failure') {
                this.alertType = 'success';
                this.message = 'Saved Successfully!';
                this.iconName = 'done';
                this.alertEnable3 = true;
                if (this.ITSMToolNames.includes(this.toolName)) {
                  this.toolName = this.toolName;
                } else {
                  this.toolName = 'Others';
                  this.toolNameOthers = json_data2['url'];
                }
              }
            });
        } else {
          this.alertType = 'warning';
          this.message = 'Please enter a valid URL';
          this.iconName = 'clear';
          this.alertEnable3 = true;
          return;
        }
      }
      else {
        this.alertEnable3 = false;
      }
    }
    if (this.lastsourceChosen == 'File Server') {
      let json_data1 = {};
      this.fileFormat = /^(?:[\w]\:|\\)(\\[a-z_\-\s0-9\.]+)+\.(txt|gif|pdf|doc|docx|xls|xlsx)$/;
      if (this.filePath == undefined || this.filePath == '') {
        this.alertType = 'warning';
        this.message = 'Please enter file server path';
        this.iconName = 'clear';
        this.alertEnable3 = true;
        return;
      }
      if (!this.fileFormat.test(String(this.filePath.trim().toLowerCase()))) {
        this.alertType = 'warning';
        this.message = 'Please enter a valid file server path';
        this.iconName = 'clear';
        this.alertEnable3 = true;
        return;
      }
      if (this.fileServerStatus && !(this.filePath.length == 0)) {
        json_data1['url'] = this.filePath.trim();
        json_data1['source'] = this.lastsourceChosen;
        if (!(json_data1['url'].length == 0)) {
          this.httpClient.post("/api/insertFileSourceDetails", json_data1, { responseType: 'text' })
            .subscribe(data => {
              this.alertType = 'success';
              this.message = 'Saved Successfully!';
              this.iconName = 'done';
              this.alertEnable3 = true;
            });
        }
      }
      else {
        this.alertEnable3 = false;
      }
    }
    if (this.lastsourceChosen == 'Sharepoint') {
      let json_data = {};
      this.urlFormat = /^((https?|ftp|smtp):\/\/)?(www.)?[a-z0-9]+(\.[a-z]{2,}){1,3}(#?\/?[a-zA-Z0-9#]+)*\/?(\?[a-zA-Z0-9-_]+=[a-zA-Z0-9-%]+&?)?$/;
      if (this.sharepointUrl == '' || this.sharepointUrl == undefined) {
        this.alertType = 'warning';
        this.message = 'Please enter Sharepoint URL';
        this.iconName = 'clear';
        this.alertEnable3 = true;
        return;
      }
      if (!this.urlFormat.test(String(this.sharepointUrl))) {
        this.alertType = 'warning';
        this.message = 'Please enter a valid Sharepoint URL';
        this.iconName = 'clear';
        this.alertEnable3 = true;
        return;
      }
      else {
        this.alertEnable3 = false;
      }
      if (this.sharepointStatus && !(this.sharepointUrl.length == 0)) {
        json_data['url'] = this.sharepointUrl.trim()
        json_data['source'] = this.lastsourceChosen;
        if (!(json_data['url'].length == 0)) {
          this.httpClient.post("/api/insertSharepointSourceDetails", json_data, { responseType: 'text' })
            .subscribe(data => {
              this.alertType = 'success';
              this.message = 'Saved Successfully!';
              this.iconName = 'done';
              this.alertEnable3 = true;
            });
        }
      }
      else {
        this.alertEnable3 = false;
      }
    }
  }
  getPredictedFieldsList() {
    this.predictedFields = [];
    this.httpClient.get('/api/predictedfields/' + this.customerID + '/' + this.chosenTeam).subscribe(data => {
      if (data) {
        data['FieldSelections'].forEach((selection) => {
          if (selection['FieldsStatus'] == "Approved") {
            let temp = selection['PredictedFields'];
            temp.forEach((field) => {
              this.predictedFields.push({ 'predictedField': field.PredictedFieldName });
            });
          } else {
            console.log('Field Status is not approved!');
          }
        });
      } else {
        console.log('Could not get predicted fields!');
      }
    }, err => {
      console.log('Could not get predicted fields! Plese try again later.');
    });
  }
  saveRTConfig() {
    if (this.RTChosenAlgorithm)
      this.httpClient.put('/api/updateRTChosenAlgorithm/' + this.RTChosenAlgorithm, null, { responseType: 'text' }).subscribe(data => {
        if (data == 'success') alert('Saved successfully!');
        else alert('Could not Save!');
      });
  }
}
