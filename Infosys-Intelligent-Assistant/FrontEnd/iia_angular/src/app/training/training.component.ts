/* Copyright 2022 Infosys Ltd.Use of this source code is governed by MIT license that can be found in the LICENSE file or athttps://opensource.org/licenses/MIT.*/
import { Component, OnInit, Input, ViewChild, ElementRef } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { NgForm } from '@angular/forms';
import { Router } from '@angular/router';
import { MatDialog } from '@angular/material';
import { MatRadioChange } from "@angular/material/radio";
import { MatExpansionPanel } from "@angular/material/expansion";
import { TuningOptionComponent } from './tuning-option/tuning-option.component';
import { NgbModal } from '@ng-bootstrap/ng-bootstrap';
import { WarningPopupComponent } from './warning-popup/warning-popup.component';
@Component({
  selector: 'training',
  templateUrl: './training.component.html',
  styleUrls: ['./training.component.css']
})
export class TrainingComponent implements OnInit {
  message = '';
  trainingMode: string = 'IIA';
  @ViewChild('trainingData') fileInput: ElementRef;
  @ViewChild('reuploadTrainingData') reuploadfileInput: ElementRef;
  panelOpenState = false;
  postResult: any = "";
  customerId: number = 1;
  uploadTrainingSuccess: boolean = false;
  attributeList = [];
  trainingId: number;
  datasetName: string = "";
  datasetExists: boolean = false;
  datasetEdited: boolean = false;
  recordsAdded: boolean = false;
  predictedFields: any = [];
  selectedInputFields = [];
  selectedAdditionalfields = [];
  selectedPredictedFields = [];
  datasetCount: number;
  datasetDeleted: boolean = false;
  loading: boolean = false;
  addingRecords: boolean = false;
  teams: any = [];
  teamsNoDataset: any = [];
  selectedTeam: string = "";
  teamID: number;
  datasetID: number;
  chosenTeam: string = "";
  uniqueFieldList = [];
  selectedUniqueFields = [];
  uniqueFieldSettings = {};
  uniqueFieldSettingsEDA = {};
  predictedDropdownSettings = {};
  predictedDropdownSettingsEDA = {};
  inputDropdownSettings = {};
  inputDropdownSettingsEDA = {};
  inputDropdownList = [];
  predictedDropdownList = [];
  fieldsToBeSaved = [];
  saveSuccess: boolean = false;
  approvedAlgorithms: boolean = false;
  trainLoading: boolean = false;
  uniqueFieldsToBeSaved = [];
  confirmDelete: boolean = false;
  refreshTraining: boolean = false;
  defaultRFCParameters: any;
  RFCCriterionValues: any;
  defaultXGBParameters: any;
  XGBObjectiveValues: any;
  defaultSVCParameters: any;
  SVCKernelValues: any;
  defaultNBParameters: any;
  defaultLRParameters: any;
  RFCTrainingMode: string = "Single";
  RFCTrainingModeDepth: string = "Single";
  XGBTrainingMode: string = "Single";
  SVCTrainingMode: string = "Single";
  NBTrainingMode: string = "Single";
  LRTrainingMode: string = "Single";
  predFields: any;
  algorithmChosen: boolean;
  predictedFieldsInformation: any[];
  algorithmsInformation: any[];
  inProgressAlgorithms: boolean;
  tunedAlgorithms: boolean;
  tunedPredictedFieldsInformation: any;
  tunedAlgorithmsInformation: any;
  AdditionalfieldSettings: {};
  AdditionalfieldSettingsEDA: {};
  BestAlgorithmDetails: {};
  teamId: number;
  predictedTicketsData: any[];
  constructor(private httpClient: HttpClient, private router: Router, private modalService: NgbModal) {
    this.datasetExists = false;
    this.datasetDeleted = false;
    this.datasetEdited = false;
    this.httpClient.get('/api/getDatasetTeamNamesTraining/' + this.customerId).subscribe(data => {
      if (data['Teams'].length > 0) {
        this.datasetExists = true;
        this.selectedTeam = data['Teams'][0];
        this.datasetID = data['DatasetIDs'][0];
        this.getTeams(this.customerId);
        this.showAlgorithms();
        this.getDefaultParameters("Single", "all");
        this.httpClient.get('/api/getDatasetDetails/' + this.customerId + "/" + this.datasetID).subscribe(data => {
          if (data && data['name'] === "") {
            this.datasetExists = false;
          } else {
            this.trainingMode = data['training_mode'];
            this.datasetExists = true;
            this.datasetName = data['name'];
            this.datasetCount = data['count'];
            let temp = data['fields'];
            temp.forEach((attribute, index) => {
              this.attributeList.push({ "id": index, "Attribute": attribute });
            })
            this.uniqueFieldList = this.attributeList.slice(0);
            this.getPredictedFields();
            this.httpClient.get('/api/algorithms/' + this.customerId + "/" + this.datasetID + "/Approved").subscribe(data => {
              if (data && data['PredictedFields'] != "") {
                this.approvedAlgorithms = true;
              } else {
                this.approvedAlgorithms = false;
              }
            });
          }
        },
          err => {
            console.log(err);
            throw "";
          });
      } else {
        this.datasetExists = false;
        this.httpClient.get('/api/getNoDatasetTeamNames/' + this.customerId).subscribe(data => {
          if (data['Teams'].length > 0) {
            this.teamsNoDataset = data['Teams']; ``
          }
        });
      }
    });
  }
  getPredictedFields() {
    this.httpClient.get('/api/predictedfields/' + this.customerId + "/" + this.selectedTeam).subscribe(data => {
      if (data != null && data != "" && data['FieldSelections'] != "" && data['UniqueFields'] != "" && data['BestAlgoParams'] != '') {
        data['FieldSelections'].forEach((selection) => {
          if (selection['FieldsStatus'] == "Approved") {
            let temp = selection['PredictedFields'];
            temp.forEach((field) => {
              let x = this.attributeList.find(attribute => attribute.Attribute === field.PredictedFieldName);
              let index = this.attributeList.indexOf(x);
              let temp1 = [];
              let temp2 = [];
              this.selectedPredictedFields.push({ "id": index, "Attribute": field.PredictedFieldName });
              field.InputFields.forEach((input, i) => {
                let x = this.attributeList.find(attribute => attribute.Attribute === input);
                let index = this.attributeList.indexOf(x);
                temp1.push({ "id": index, "Attribute": input });
              });
              field.Additionalfields.forEach((input, i) => {
                let x = this.attributeList.find(attribute => attribute.Attribute === input);
                let index = this.attributeList.indexOf(x);
                temp2.push({ "id": index, "Attribute": input });
              });
              this.selectedAdditionalfields[field.PredictedFieldName] = temp2;
              this.selectedInputFields[field.PredictedFieldName] = temp1;
            })
          }
        });
        if (this.selectedPredictedFields.length > 0) {
          this.predictedDropdownList = this.attributeList.slice(0);
          data['UniqueFields'].forEach((field) => {
            let x = this.attributeList.find(attribute => attribute.Attribute === field.FieldName);
            let index = this.attributeList.indexOf(x);
            let temp1 = [];
            this.selectedUniqueFields.push({ "id": index, "Attribute": field.FieldName });
          });
          this.BestAlgorithmDetails = data['BestAlgoParams'];
        } else {
          this.predictedDropdownList = this.attributeList.slice(0);
        }
        this.httpClient.get('/api/algorithms/' + this.customerId + "/" + this.datasetID + "/Approved").subscribe(data => {
          if (data && data['PredictedFields'] != "") {
            this.approvedAlgorithms = true;
          } else {
            this.approvedAlgorithms = false;
          }
        });
      } else {
        this.predictedDropdownList = this.attributeList.slice(0);
      }
    });
  }
  ngOnInit() {
    this.uniqueFieldSettings = {
      singleSelection: false,
      labelKey: "Attribute",
      text: "Select Unique Fields",
      selectAllText: 'Select All',
      unSelectAllText: 'Unselect All',
      enableSearchFilter: true,
      maxHeight: 500,
      classes: "myclass custom-class",
    };
    this.uniqueFieldSettingsEDA = {
      singleSelection: false,
      labelKey: "Attribute",
      maxHeight: 500,
      classes: "myclass custom-class disabled",
      disabled: true,
    };
    this.inputDropdownSettingsEDA = {
      singleSelection: false,
      labelKey: "Attribute",
      maxHeight: 500,
      classes: "myclass custom-class disabled",
      disabled: true,
    };
    this.inputDropdownSettings = {
      singleSelection: false,
      labelKey: "Attribute",
      text: "Select Input Fields",
      selectAllText: 'Select All',
      unSelectAllText: 'Unselect All',
      enableSearchFilter: true,
      maxHeight: 500,
      classes: "myclass custom-class",
      enableFilterSelectAll: false,
    };
    this.predictedDropdownSettingsEDA = {
      singleSelection: false,
      labelKey: "Attribute",
      maxHeight: 500,
      classes: "myclass custom-class disabled",
      disabled: true,
    };
    this.predictedDropdownSettings = {
      singleSelection: false,
      labelKey: "Attribute",
      text: "Select Predicted Fields",
      selectAllText: 'Select All',
      unSelectAllText: 'Unselect All',
      enableSearchFilter: true,
      maxHeight: 500,
      classes: "myclass custom-class",
    };
    this.AdditionalfieldSettingsEDA = {
      singleSelection: false,
      labelKey: "Attribute",
      text: "Select Additional Fields",
      maxHeight: 500,
      classes: "myclass custom-class disabled",
      disabled: true,
      noDataLabel: 'No Data Available'
    };
    this.AdditionalfieldSettings = {
      singleSelection: false,
      labelKey: "Attribute",
      text: "Select Additional Fields",
      selectAllText: 'Select All',
      unSelectAllText: 'Unselect All',
      enableSearchFilter: true,
      maxHeight: 500,
      classes: "myclass custom-class",
    };
  }
  private teamChange() {
    this.httpClient.get('/api/getTeamID/' + this.customerId + '/' + this.chosenTeam).subscribe(data => {
      if (data != 'failure') {
        this.teamId = Number(data);
        this.httpClient.get('/api/getDatasetID/' + this.customerId + '/' + this.teamId).subscribe(data => {
          if (data != '-1') {
            this.datasetID = Number(data);
            this.getPredictedFields();
          }
        });
      }
    });
  }
  uploadTrainingData() {
    this.datasetDeleted = false;
    this.datasetEdited = false;
    this.datasetExists = false;
    this.uploadTrainingSuccess = false;
    this.attributeList = [];
    this.trainingMode = 'IIA';
    const fileBrowser = this.fileInput.nativeElement;
    let temp = [];
    if (fileBrowser.files && fileBrowser.files[0]) {
      if (fileBrowser.files[0].type == 'text/csv' || fileBrowser.files[0].type == "application/x-zip-compressed" || fileBrowser.files[0].type == "application/vnd.ms-excel") {
        this.loading = true;
        const formData = new FormData();
        formData.append('trainingData', fileBrowser.files[0]);
        this.httpClient.post('/api/uploadTrainingData/' + this.customerId + '/' + this.chosenTeam + "/" + this.chosenTeam + "/" + this.trainingMode, formData, { responseType: 'text' })
          .subscribe(data => {
            if (data == "success") {
              this.loading = false;
              this.uploadTrainingSuccess = true;
              this.datasetExists = true;
              this.postResult = 'Training data uploaded successfully!';
              this.getTeams(this.customerId);
              this.httpClient.get('/api/getTeamID/' + this.customerId + "/" + this.chosenTeam).subscribe(data => {
                this.teamID = parseInt(data.toString());;
                this.httpClient.get('/api/getDatasetID/' + this.customerId + "/" + this.teamID).subscribe(data => {
                  this.datasetID = parseInt(data.toString());
                  this.httpClient.get('/api/getDatasetDetails/' + this.customerId + "/" + this.datasetID).subscribe(data => {
                    this.selectedTeam = this.chosenTeam;
                    this.datasetName = data['name'];
                    this.datasetCount = data['count'];
                    this.trainingMode = data['training_mode']
                    temp = data['fields'];
                    temp.forEach((attribute, index) => {
                      this.attributeList.push({ "id": index, "Attribute": attribute });
                    });
                    this.uniqueFieldList = this.attributeList.slice(0);
                    this.predictedDropdownList = this.attributeList.slice(0);
                    // this.getDataSetID();
                    this.getPredictedFields();
                    this.showAlgorithms();
                    // this.inputDropdownList = this.attributeList.slice(0);
                  },
                    err => {
                      this.loading = false;
                      console.log(err);
                      throw "";
                    });
                });
              });
            } else {
              this.loading = false;
              alert("couldn't upload the file! please try again");
            }
          });
      } else {
        alert("Please attach Zip/CSV file");
      }
    }
  }
  private getCustomerID(custName: string) {
    //get customer ID based on name from TblCustomer
    this.httpClient.get('/api/customer/' + custName).subscribe(data => {
      this.customerId = parseInt(data.toString());
    });
  }
  private valueChange() {
    this.datasetName = "";
    this.datasetCount = 0;
    this.attributeList = [];
    this.selectedPredictedFields = [];
    this.selectedInputFields = [];
    this.selectedUniqueFields = [];
    this.selectedAdditionalfields = []
    this.datasetID = -1;
    this.approvedAlgorithms = false;
    this.httpClient.get('/api/getTeamID/' + this.customerId + "/" + this.selectedTeam).subscribe(data => {
      this.teamID = parseInt(data.toString());;
      this.httpClient.get('/api/getDatasetID/' + this.customerId + "/" + this.teamID).subscribe(data => {
        if (data == -1) {
          this.datasetExists = false;
          this.httpClient.get('/api/getNoDatasetTeamNames/' + this.customerId).subscribe(data => {
            if (data['Teams'].length > 0) {
              this.teamsNoDataset = data['Teams'];
            }
          });
        } else {
          this.datasetID = parseInt(data.toString());
          this.httpClient.get('/api/getDatasetDetails/' + this.customerId + "/" + this.datasetID).subscribe(data => {
            if (data && data['name'] === "") {
              this.datasetExists = false;
              this.httpClient.get('/api/getNoDatasetTeamNames/' + this.customerId).subscribe(data => {
                if (data['Teams'].length > 0) {
                  this.teamsNoDataset = data['Teams'];
                }
              });
            } else {
              this.trainingMode = data['training_mode'];
              this.datasetExists = true;
              this.datasetName = data['name'];
              this.datasetCount = data['count'];
              let temp = data['fields'];
              temp.forEach((attribute, index) => {
                this.attributeList.push({ "id": index, "Attribute": attribute });
              })
              this.uniqueFieldList = this.attributeList.slice(0);
              this.httpClient.get('/api/predictedfields/' + this.customerId + "/" + this.selectedTeam).subscribe(data => {
                if (data != null && data != "" && data['FieldSelections'] != "" && data['UniqueFields'] != "") {
                  data['FieldSelections'].forEach((selection) => {
                    if (selection['FieldsStatus'] == "Approved") {
                      let temp = selection['PredictedFields'];
                      temp.forEach((field) => {
                        let x = this.attributeList.find(attribute => attribute.Attribute === field.PredictedFieldName);
                        let index = this.attributeList.indexOf(x);
                        let temp1 = [];
                        let temp2 = [];
                        this.selectedPredictedFields.push({ "id": index, "Attribute": field.PredictedFieldName });
                        field.InputFields.forEach((input, i) => {
                          let x = this.attributeList.find(attribute => attribute.Attribute === input);
                          let index = this.attributeList.indexOf(x);
                          temp1.push({ "id": index, "Attribute": input });
                        });
                        field.Additionalfields.forEach((input, i) => {
                          let x = this.attributeList.find(attribute => attribute.Attribute === input);
                          let index = this.attributeList.indexOf(x);
                          temp2.push({ "id": index, "Attribute": input });
                        });
                        this.selectedAdditionalfields[field.PredictedFieldName] = temp2;
                        this.selectedInputFields[field.PredictedFieldName] = temp1;
                      })
                    }
                  });
                  if (this.selectedPredictedFields.length > 0) {
                    this.predictedDropdownList = this.attributeList.slice(0);
                    // this.inputDropdownList = this.attributeList.slice(0);
                    data['UniqueFields'].forEach((field) => {
                      let x = this.attributeList.find(attribute => attribute.Attribute === field.FieldName);
                      let index = this.attributeList.indexOf(x);
                      let temp1 = [];
                      this.selectedUniqueFields.push({ "id": index, "Attribute": field.FieldName });
                    });
                  } else {
                    this.predictedDropdownList = this.attributeList.slice(0);
                    // this.inputDropdownList = this.attributeList.slice(0);
                  }
                } else {
                  this.predictedDropdownList = this.attributeList.slice(0);
                  // this.inputDropdownList = this.attributeList.slice(0);
                }
              });
              this.httpClient.get('/api/algorithms/' + this.customerId + "/" + this.datasetID + "/Approved").subscribe(data => {
                if (data && data['PredictedFields'] != "") {
                  this.approvedAlgorithms = true;
                } else {
                  this.approvedAlgorithms = false;
                }
              });
            }
          },
            err => {
              console.log(err);
              throw "";
            });
        }
      },
        err => {
          console.log(err);
          throw "";
        });
    },
      err => {
        console.log(err);
        throw "";
      });
  }
  private getTeams(custID) {
    this.httpClient.get('/api/getTeams/' + this.customerId).subscribe(data => {
      this.teams = data['Teams'];
    });
  }
  private addRecords() {
    this.datasetEdited = true;
  }
  appendRecords() {
    this.recordsAdded = false;
    const fileBrowser = this.fileInput.nativeElement;
    if (fileBrowser.files[0].type != 'text/csv' && fileBrowser.files[0].type != "application/vnd.ms-excel") {
      this.recordsAdded = false;
      alert("Please upload CSV File");
      return;
    }
    let temp = [];
    if (fileBrowser.files[0].type == 'text/csv' || fileBrowser.files[0].type == "application/vnd.ms-excel") {
      if (fileBrowser.files && fileBrowser.files[0]) {
        this.addingRecords = true;
        const formData = new FormData();
        formData.append('trainingData', fileBrowser.files[0]);
        this.loading = true;
        this.httpClient.post('/api/uploadTrainingData/' + this.customerId + "/" + this.selectedTeam + "/" + this.selectedTeam + "/" + this.trainingMode, formData, { responseType: 'text' })
          .subscribe(data => {
            this.loading = false;
            if (data == 'success') {
              this.addingRecords = false;
              this.httpClient.get('/api/getTeamID/' + this.customerId + "/" + this.selectedTeam).subscribe(data => {
                this.teamID = parseInt(data.toString());;
                this.httpClient.get('/api/getDatasetID/' + this.customerId + "/" + this.teamID).subscribe(data => {
                  this.datasetID = parseInt(data.toString());
                  this.httpClient.get('/api/getDatasetDetails/' + this.customerId + "/" + this.datasetID).subscribe(data => {
                    this.datasetCount = data['count'];
                  });
                });
              });
              this.recordsAdded = true;
              this.message = "New records added successfully!";
            } else if (data == 'failure') {
              this.recordsAdded = true;
              this.message = 'Upload failed, please upload the right dataset with matching columns';
            } else {
              this.recordsAdded = true;
              this.message = data;
            }
          },
            err => {
              this.loading = false;
              console.log(err);
              throw "";
            });
      } else {
        this.addingRecords = false;
      }
    }
  }
  deleteDataset() {
    this.datasetDeleted = false;
    this.datasetEdited = false;
    this.uploadTrainingSuccess = false;
    this.approvedAlgorithms = false;
    this.selectedTeam = "";
    this.chosenTeam = "";
    this.httpClient.delete('/api/deleteDataset/' + this.customerId + "/" + this.datasetID, { responseType: 'text' })
      .subscribe(data => {
        this.datasetDeleted = true;
        this.datasetExists = false;
        this.datasetName = "";
        this.selectedInputFields = [];
        this.selectedPredictedFields = [];
        this.selectedUniqueFields = [];
        this.router.navigateByUrl('').then(e => {
          if (e) {
            this.httpClient.get('/api/getNoDatasetTeamNames/' + this.customerId).subscribe(data => {
              if (data['Teams'].length > 0) {
                this.teamsNoDataset = data['Teams'];
              }
            });
          } else {
            console.log("Navigation has failed!");
          }
        });
      },
        err => {
          console.log(err);
          throw "";
        });
  }
  //ngonchange()
  deleteTrainingRecords() {
    const fileBrowser = this.reuploadfileInput.nativeElement;
    let temp = [];
    if (fileBrowser.files && fileBrowser.files[0]) {
      this.loading = true;
      const formData = new FormData();
      formData.append('trainingData', fileBrowser.files[0]);
      this.httpClient.post('/api/deleteTrainingRecords/' + this.customerId + "/" + this.datasetID + "/" + this.selectedTeam, formData, { responseType: 'json' })
        .subscribe(data => {
          if (data['status'] == "success") {
            this.loading = false;
            this.refreshTraining = true;
            document.getElementById("close").click();
            this.ngOnInit();
          } else {
            this.loading = false;
          }
          this.httpClient.get('/api/getDatasetDetails/' + this.customerId + "/" + this.datasetID).subscribe(data => {
            this.datasetCount = data['count'];
          });
          this.router.navigateByUrl('').then(e => {
            if (e) {
              this.httpClient.get('/api/getNoDatasetTeamNames/' + this.customerId).subscribe(data => {
                if (data['Teams'].length > 0) {
                  this.teamsNoDataset = data['Teams'];
                }
              });
            } else {
              console.log("Navigation has failed!");
            }
          });
        }, err => {
          this.loading = false;
          console.log(err);
          throw "";
        });
    }
  }
  saveFieldSelections() {
    let selectedField;
    let predictFieldsToBeSaved = [];
    this.fieldsToBeSaved = [];
    this.uniqueFieldsToBeSaved = [];
    this.selectedPredictedFields.forEach(field => {
      let inputFields = [];
      let additionalFields = [];
      let predictInputFields = [];
      let usePredFieldFlag = 'false';
      if (Object.keys(this.selectedInputFields).length > 0) {
        this.selectedInputFields[field.Attribute].forEach(field => {
          selectedField = field.Attribute;
          if (selectedField.slice(0, 10) == 'predicted_') {
            selectedField = selectedField.slice(10);
            predictInputFields.push(selectedField);
            usePredFieldFlag = 'true';
          }
          inputFields.push(selectedField);
        });
      }
      if (Object.keys(this.selectedAdditionalfields).length > 0) {
        this.selectedAdditionalfields[field.Attribute].forEach(field => {
          selectedField = field.Attribute;
          if (selectedField.slice(0, 10) == 'predicted_') {
            selectedField = selectedField.slice(10);
            predictInputFields.push(selectedField);
            usePredFieldFlag = 'true';
          }
          additionalFields.push(selectedField);
        });
      }
      if (predictInputFields.length > 0)
        predictFieldsToBeSaved.push({ "PredictValue": field.Attribute, "DepPredictValue": predictInputFields });
      this.fieldsToBeSaved.push({ 'PredictedFieldName': field.Attribute, 'usePredFieldFlag': usePredFieldFlag, 'InputFields': inputFields, 'Additionalfields': additionalFields });
    });
    this.selectedUniqueFields.forEach(field => {
      this.uniqueFieldsToBeSaved.push({ 'FieldName': field.Attribute });
    })
    let data = {};
    let datas = {};
    data['FieldSelections'] = this.fieldsToBeSaved;
    data['UniqueFields'] = this.uniqueFieldsToBeSaved;
    data['DependedPredict'] = predictFieldsToBeSaved;
    this.loading = true;
    this.httpClient.put('/api/saveFieldSelections/' + this.customerId + "/" + this.datasetID, data, { responseType: 'text', headers: { 'Content-Type': 'application/json' } })
      .subscribe(msg => {
        datas = JSON.parse(msg);
        this.loading = false;
        this.saveSuccess = true;
        let dataPassToChild: any = {};
        dataPassToChild['DatasetID'] = 1;
        dataPassToChild['Threshold'] = datas['Threshold selected'];
        dataPassToChild['PredictedFields'] = datas['Predicted fields below threshold'];
        dataPassToChild['Message'] = datas['Message'];
        let msg1 = 'Classes having less number of tickets:\n' + datas['Classes having less number of tickets'];
        if (datas['Warning'] == true) {
          alert(msg1 + '\n' + datas['Message']);
        }
      },
        err => {
          this.loading = false;
          console.log(err);
          throw "";
        });
  }
  train() {
    this.trainLoading = true;
    let data = {};
    data['Status'] = "Train";
    this.httpClient.post('/api/train/' + this.customerId + "/" + this.datasetID, data).subscribe(data => {
      this.trainLoading = false;
      this.trainingId = parseInt(data.toString());
      this.router.navigate(['/algorithminformation', this.datasetID]);
    });
  }
  getApprovedAlgorithms() {
    this.router.navigate(['/algorithminformation', this.datasetID]);
  }
  onUniqueFieldSelect(item: any) {
  }
  onUniqueFieldDeSelect(item: any) {
  }
  onInputSelectAll(items: any, predictField: string) {
    items.forEach((fieldAttr) => {
      this.onInputSelect(fieldAttr['Attribute'], predictField);
    })
  }
  onInputSelect(selectedField: string, predictField: string) {
    if (selectedField.slice(0, 10) == 'predicted_')
      selectedField = selectedField.slice(10);
    else
      selectedField = 'predicted_' + selectedField
    for (let field of this.selectedInputFields[predictField])
      if (field.Attribute == selectedField) {
        this.selectedInputFields[predictField].splice(this.selectedInputFields[predictField].indexOf(field), 1);
        break;
      }
  }
  ngOnDestroy() {
    this.datasetDeleted = false;
    this.datasetEdited = false;
    this.datasetExists = false;
    this.recordsAdded = false;
    this.uploadTrainingSuccess = false;
  }
  onOpenCsearch(Rfield) {
    this.inputDropdownList = this.attributeList.slice(0);
    // this.inputDropdownList = Object.assign([], this.CopyinputDropdownList);
    let temp = this.inputDropdownList.find(deselectedField => deselectedField.Attribute === Rfield);
    let index = this.inputDropdownList.indexOf(temp);
    this.inputDropdownList.splice(index, 1);
    let predictFieldsArray = Array(this.selectedPredictedFields)[0];
    if (predictFieldsArray.length > 1) {
      let predictField;
      let index;
      let optionsLst = [];
      let serachList = ['predicted_' + Rfield];
      let indexCount = this.inputDropdownList.length;
      for (let fieldDoc of predictFieldsArray) {
        if (fieldDoc.Attribute != Rfield)
          optionsLst.push(fieldDoc.Attribute);
      }
      // -- Logic to choose the predict field available for selection as input field --
      for (let i = 0; i < predictFieldsArray.length - 1; i++) {
        for (let fieldDoc of predictFieldsArray) {
          if (optionsLst.length > 0) {
            predictField = fieldDoc.Attribute;
            if (predictField != Rfield && this.selectedInputFields[predictField])
              for (let inputField of this.selectedInputFields[predictField]) {
                if (serachList.indexOf(inputField.Attribute) >= 0) {
                  index = optionsLst.indexOf(predictField)
                  if (index >= 0) {
                    optionsLst.splice(index, 1);
                    serachList.push('predicted_' + predictField);
                    break;
                  }
                }
              }
          }
        }
      }
      if (optionsLst.length > 0)
        for (let fieldName of optionsLst) {
          indexCount++;
          this.inputDropdownList.push({ 'id': indexCount, 'Attribute': 'predicted_' + fieldName });
          if (this.selectedInputFields[Rfield])
            for (let inputField of this.selectedInputFields[Rfield])
              if (inputField.Attribute == 'predicted_' + fieldName) inputField.id = indexCount;
        }
    }
  }
  onChange(radio: MatRadioChange, panel: MatExpansionPanel) {
    panel.open();
  }
  private getDefaultParameters(parameterType: string, algoName: string) {
    this.httpClient.get('/api/getAlgoDefaultParams/' + this.customerId + "/" + this.datasetID + "/" + parameterType).subscribe(data => {
      let temp = data['Algorithms'];
      if (algoName == "RandomForestClassifier") {
        temp.forEach(algorithm => {
          if (algorithm['AlgorithmName'] == "RandomForestClassifier") {
            this.defaultRFCParameters = algorithm['Parameters'];
            this.httpClient.get('/api/getDropdownParams/' + algorithm['AlgorithmName']).subscribe(data => {
              if (data && data['ParameterName'] == "criterion") {
                this.RFCCriterionValues = data['Value'];
              }
            });
          }
        });
      } else if (algoName == "XGBClassifier") {
        temp.forEach(algorithm => {
          if (algorithm['AlgorithmName'] == "XGBClassifier") {
            this.defaultXGBParameters = algorithm['Parameters'];
            this.httpClient.get('/api/getDropdownParams/' + algorithm['AlgorithmName']).subscribe(data => {
              if (data && data['ParameterName'] == "objective") {
                this.XGBObjectiveValues = data['Value'];
              }
            });
          }
        });
      } else if (algoName == "SVC") {
        temp.forEach(algorithm => {
          if (algorithm['AlgorithmName'] == "SVC") {
            this.defaultSVCParameters = algorithm['Parameters'];
            this.httpClient.get('/api/getDropdownParams/' + algorithm['AlgorithmName']).subscribe(data => {
              if (data && data['ParameterName'] == "kernel") {
                this.SVCKernelValues = data['Value'];
              }
            });
          }
        });
      } else if (algoName == "MultinomialNB") {
        temp.forEach(algorithm => {
          if (algorithm['AlgorithmName'] == "MultinomialNB") {
            this.defaultNBParameters = algorithm['Parameters'];
          }
        });
      } else if (algoName == "LogisticRegression") {
        temp.forEach(algorithm => {
          if (algorithm['AlgorithmName'] == "LogisticRegression") {
            this.defaultLRParameters = algorithm['Parameters'];
          }
        });
      } else if (algoName == "all") {
        if (temp != undefined) {
          temp.forEach(algorithm => {
            if (algorithm['AlgorithmName'] == "RandomForestClassifier") {
              this.defaultRFCParameters = algorithm['Parameters'];
              this.httpClient.get('/api/getDropdownParams/' + algorithm['AlgorithmName']).subscribe(data => {
                if (data && data[0]['ParameterName'] == "criterion") {
                  this.RFCCriterionValues = data[0]['Value'];
                }
              });
            } else if (algorithm['AlgorithmName'] == "XGBClassifier") {
              this.defaultXGBParameters = algorithm['Parameters'];
              this.httpClient.get('/api/getDropdownParams/' + algorithm['AlgorithmName']).subscribe(data => {
                if (data && data[0]['ParameterName'] == "objective") {
                  this.XGBObjectiveValues = data[0]['Value'];
                }
              });
            } else if (algorithm['AlgorithmName'] == "SVC") {
              this.defaultSVCParameters = algorithm['Parameters'];
              this.httpClient.get('/api/getDropdownParams/' + algorithm['AlgorithmName']).subscribe(data => {
                if (data && data[0]['ParameterName'] == "kernel") {
                  this.SVCKernelValues = data[0]['Value'];
                }
              });
            } else if (algorithm['AlgorithmName'] == "MultinomialNB") {
              this.defaultNBParameters = algorithm['Parameters'];
            } else if (algorithm['AlgorithmName'] == "LogisticRegression") {
              this.defaultLRParameters = algorithm['Parameters'];
            }
          });
        }
      }
    });
  }
  openAdvancedSettingModal() {
    const modalRef = this.modalService.open(TuningOptionComponent, { ariaLabelledBy: 'modal-basic-title', size: "lg" });
    modalRef.componentInstance.closeResult = true;
    modalRef.componentInstance.tagCloudData = [];
    modalRef.componentInstance.Summaries = [];
    modalRef.componentInstance.customerId = this.customerId;
    modalRef.componentInstance.datasetID = this.datasetID;
    if (this.predFields != null && this.predFields.length > 0) {
      this.predFields.forEach(element => {
        modalRef.componentInstance.Summaries.push(element.Name.toString());
      });
      modalRef.componentInstance.predicted_field = this.predFields[0].Name.toString();
      modalRef.componentInstance.drawGraph();
    }
  }
  private showAlgorithms() {
    this.algorithmChosen = true;
    this.predictedFieldsInformation = [];
    this.algorithmsInformation = [];
    this.httpClient.get('/api/algorithms/' + this.customerId + "/" + this.datasetID + "/InProgress").subscribe(data => {
      this.inProgressAlgorithms = true;
      if (data && data['PredictedFields'] != "") {
        this.predictedFieldsInformation = data['PredictedFields'];
        this.predFields = data['PredictedFields'];
        this.predictedFieldsInformation.forEach((predictedField, index) => {
          this.algorithmsInformation.push(predictedField['Algorithms']);
        });
      } else {
        this.inProgressAlgorithms = false;
      }
    })
    this.httpClient.get('/api/algorithms/' + this.customerId + "/" + this.datasetID + "/Tuning").subscribe(data => {
      if (data && data['PredictedFields'] != "") {
        this.tunedAlgorithms = true;
        this.tunedPredictedFieldsInformation = data['PredictedFields'];
        this.tunedPredictedFieldsInformation.forEach((tunedPredictedField, index) => {
          this.tunedAlgorithmsInformation.push(tunedPredictedField['Algorithms']);
        });
      } else {
        this.tunedAlgorithms = false;
      }
    })
    if (this.predFields == null || this.predFields.length == 0) {
      this.httpClient.get('/api/algorithms/' + this.customerId + "/" + this.datasetID + "/Approved").subscribe(data => {
        if (data && data['PredictedFields'] != "") {
          this.predFields = data['PredictedFields'];
        }
      });
    }
  }
  getMoreInformation(): string {
    return '1. Please do not include the Predicted Fields, Textual Input Fields and Numeric fields (ex: date time etc).\n2. For additional columns one may refer to EDA Advanced Report or can be left empty.';
  }
}