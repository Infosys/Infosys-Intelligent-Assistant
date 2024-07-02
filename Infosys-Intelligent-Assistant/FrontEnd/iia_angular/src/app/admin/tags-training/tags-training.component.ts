/* Copyright 2022 Infosys Ltd.Use of this source code is governed by MIT license that can be found in the LICENSE file or athttps://opensource.org/licenses/MIT.*/
import { Component, OnInit, Input, ViewChild, ElementRef } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { NgForm } from '@angular/forms';
import { Router } from '@angular/router';
@Component({
  selector: 'app-tags-training',
  templateUrl: './tags-training.component.html',
  styleUrls: ['./tags-training.component.css']
})
export class TagsTrainingComponent implements OnInit {
  @ViewChild('trainingData') fileInput: ElementRef;
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
  selectedInputFields = {};
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
  selectedUniqueFields = [];
  uniqueFieldSettings = {};
  predictedDropdownSettings = {};
  inputDropdownSettings = {};
  inputDropdownList = [];
  predictedDropdownList = [];
  fieldsToBeSaved = [];
  saveSuccess: boolean = false;
  approvedAlgorithms: boolean = false;
  trainLoading: boolean = false;
  uniqueFieldsToBeSaved = [];
  trainSuccess: boolean = false;
  disableTeam: boolean = false;
  constructor(private httpClient: HttpClient, private router: Router) {
    this.datasetExists = false;
    this.datasetDeleted = false;
    this.datasetEdited = false;
    this.httpClient.get('/api/getTagDatasetTeamNames/' + this.customerId).subscribe(data => {
      if (data['Teams'].length > 0) {
        this.datasetExists = true;
        this.selectedTeam = data['Teams'][0];
        this.datasetID = data['TagsDatasetIDs'][0];
        this.getTeams(this.customerId);
        this.httpClient.get('/api/getTagsDatasetDetails/' + this.customerId + "/" + this.datasetID).subscribe(data => {
          if (data && data['name'] === "") {
            this.datasetExists = false;
          } else {
            this.datasetExists = true;
            this.datasetName = data['name'];
            this.datasetCount = data['count'];
            let temp = data['fields'];
            temp.forEach((attribute, index) => {
              this.attributeList.push({ "id": index, "Attribute": attribute });
            })
            let temp_list: any = []
            this.httpClient.get('/api/getTagBasedField/' + this.customerId + "/" + this.datasetID).subscribe(data => {
              console.log('in showInputOutput');
              if (data != null && data != "" && data['TagBasedField'] != "" && data != 'Failure') {
                temp_list = data['TagBasedField'];
                temp_list.forEach(element => {
                  this.selectedUniqueFields.push({ "id": temp_list.indexOf(element), "Attribute": element });
                });
              } else {
                this.predictedDropdownList = this.attributeList.slice(0);
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
        this.httpClient.get('/api/getNoTagDatasetTeamNames/' + this.customerId).subscribe(data => {
          if (data['Teams'].length > 0) {
            this.teamsNoDataset = data['Teams'];
          } else {
            this.disableTeam = true;
          }
        });
      }
    });
  }
  ngOnInit() {
    this.uniqueFieldSettings = {
      singleSelection: true,
      labelKey: "Attribute",
      text: "Select Unique Fields",
      selectAllText: 'Select All',
      unSelectAllText: 'Unselect All',
      enableSearchFilter: true,
      maxHeight: 500,
      classes: "myclass custom-class"
    };
  }
  private teamChange() {
  }
  uploadTrainingData() {
    if (this.chosenTeam.length != 0) {
      this.datasetDeleted = false;
      this.datasetEdited = false;
      this.datasetExists = false;
      this.uploadTrainingSuccess = false;
      this.attributeList = [];
      const fileBrowser = this.fileInput.nativeElement;
      let temp = [];
      if (fileBrowser.files && fileBrowser.files[0]) {
        this.loading = true;
        const formData = new FormData();
        formData.append('trainingData', fileBrowser.files[0]);
        this.httpClient.post('/api/uploadTagsTrainingData/' + this.customerId + '/' + this.chosenTeam + "/" + this.chosenTeam, formData, { responseType: 'text' })
          .subscribe(data => {
            if (data == "success") {
              this.loading = false;
              this.uploadTrainingSuccess = true;
              this.datasetExists = true;
              this.postResult = 'Training data uploaded successfully!';
              this.getTeams(this.customerId);
              this.httpClient.get('/api/getTagTeamID/' + this.customerId + "/" + this.chosenTeam).subscribe(data => {
                this.teamID = parseInt(data.toString());;
                this.httpClient.get('/api/getTagDatasetID/' + this.customerId + "/" + this.teamID).subscribe(data => {
                  this.datasetID = parseInt(data.toString());
                  this.httpClient.get('/api/getTagsDatasetDetails/' + this.customerId + "/" + this.datasetID).subscribe(data => {
                    this.selectedTeam = this.chosenTeam;
                    this.datasetName = data['name'];
                    this.datasetCount = data['count'];
                    temp = data['fields'];
                    temp.forEach((attribute, index) => {
                      this.attributeList.push({ "id": index, "Attribute": attribute });
                    });
                    this.predictedDropdownList = this.attributeList.slice(0);
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
      }
    } else {
      alert('Select the team')
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
    this.chosenTeam = ""
    this.datasetCount = 0;
    this.attributeList = [];
    this.selectedPredictedFields = [];
    this.selectedInputFields = [];
    this.selectedUniqueFields = [];
    this.datasetID = -1;
    this.approvedAlgorithms = false;
    this.httpClient.get('/api/getTagTeamID/' + this.customerId + "/" + this.selectedTeam).subscribe(data => {
      this.teamID = parseInt(data.toString());;
      this.httpClient.get('/api/getTagDatasetID/' + this.customerId + "/" + this.teamID).subscribe(data => {
        if (data == -1) {
          this.datasetExists = false;
          this.httpClient.get('/api/getNoTagDatasetTeamNames/' + this.customerId).subscribe(data => {
            if (data['Teams'].length > 0) {
              this.teamsNoDataset = data['Teams'];
            } else {
              this.disableTeam = true;
            }
          });
        } else {
          this.datasetID = parseInt(data.toString());
          this.httpClient.get('/api/getTagsDatasetDetails/' + this.customerId + "/" + this.datasetID).subscribe(data => {
            if (data && data['name'] === "") {
              this.datasetExists = false;
              this.httpClient.get('/api/getNoTagDatasetTeamNames/' + this.customerId).subscribe(data => {
                if (data['Teams'].length > 0) {
                  this.teamsNoDataset = data['Teams'];
                } else {
                  this.disableTeam = true;
                }
              });
            } else {
              this.datasetExists = true;
              this.datasetName = data['name'];
              this.datasetCount = data['count'];
              let temp = data['fields'];
              temp.forEach((attribute, index) => {
                this.attributeList.push({ "id": index, "Attribute": attribute });
              })
              console.log("Attribute list is " + this.attributeList);
              // this.uniqueFieldList = this.attributeList.slice(0);
              let temp_list: any = []
              this.httpClient.get('/api/getTagBasedField/' + this.customerId + "/" + this.datasetID).subscribe(data => {
                console.log('in showInputOutput');
                if (data != null && data != "" && data['TagBasedField'] != "" && data != 'Failure') {
                  temp_list = data['TagBasedField'];
                  temp_list.forEach(element => {
                    this.selectedUniqueFields.push({ "id": temp_list.indexOf(element), "Attribute": element });
                  });
                  this.trainSuccess = true;
                } else {
                  this.predictedDropdownList = this.attributeList.slice(0);
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
    this.teams = []
    if (this.selectedTeam != "") {
      this.teams.push(this.selectedTeam)
    } else {
      this.teams.push(this.chosenTeam)
    }
    this.httpClient.get('/api/getTagDatasetTeamNames/' + this.customerId).subscribe(data => {
      if (data['Teams'].length > 0) {
        data['Teams'].forEach(element => {
          if (!this.teams.includes(element)) {
            this.teams.push(element)
          }
        });
      }
    })
    this.httpClient.get('/api/getNoTagDatasetTeamNames/' + this.customerId).subscribe(data => {
      if (data['Teams'].length > 0) {
        data['Teams'].forEach(element => {
          if (!this.teams.includes(element)) {
            this.teams.push(element)
          }
        });
      }
    });
  }
  private addRecords() {
    this.datasetEdited = true;
  }
  appendRecords() {
    console.log('in appendRecords');
    console.log(this.fileInput.nativeElement.value);
    const fileBrowser = this.fileInput.nativeElement;
    let temp = [];
    if (fileBrowser.files && fileBrowser.files[0]) {
      this.addingRecords = true;
      const formData = new FormData();
      formData.append('trainingData', fileBrowser.files[0]);
      this.httpClient.post('/api/uploadTagsTrainingData/' + this.customerId + "/" + this.selectedTeam + "/" + this.selectedTeam, formData, { responseType: 'text' })
        .subscribe(data => {
          this.addingRecords = false;
          this.httpClient.get('/api/getTagTeamID/' + this.customerId + "/" + this.selectedTeam).subscribe(data => {
            this.teamID = parseInt(data.toString());;
            this.httpClient.get('/api/getTagDatasetID/' + this.customerId + "/" + this.teamID).subscribe(data => {
              this.datasetID = parseInt(data.toString());
              this.httpClient.get('/api/getTagsDatasetDetails/' + this.customerId + "/" + this.datasetID).subscribe(data => {
                this.datasetCount = data['count'];
              });
            });
          });
          this.recordsAdded = true;
        },
          err => {
            console.log(err);
            throw "";
          });
    } else {
      this.addingRecords = false;
    }
  }
  deleteDataset() {
    this.datasetDeleted = false;
    this.datasetEdited = false;
    this.uploadTrainingSuccess = false;
    this.approvedAlgorithms = false;
    this.selectedTeam = "";
    this.chosenTeam = "";
    this.httpClient.delete('/api/deleteTagDataset/' + this.customerId + "/" + this.datasetID, { responseType: 'text' })
      .subscribe(data => {
        this.datasetDeleted = true;
        this.datasetExists = false;
        this.datasetName = "";
        this.selectedInputFields = [];
        this.selectedPredictedFields = [];
        this.selectedUniqueFields = [];
        this.router.navigateByUrl('').then(e => {
          if (e) {
            this.httpClient.get('/api/getNoTagDatasetTeamNames/' + this.customerId).subscribe(data => {
              if (data['Teams'].length > 0) {
                this.teamsNoDataset = data['Teams'];
              } else {
                this.disableTeam = true;
              }
            });
          } else {
            console.log("Navigation has failed!");
          }
        });
        console.log(data);
      },
        err => {
          console.log(err);
          throw "";
        });
  }
  train() {
    console.log('in train()');
    this.trainLoading = true;
    this.httpClient.post('/api/tagTrain/' + this.customerId + "/" + this.datasetID, null, { responseType: 'text' }).subscribe(data => {
      this.trainLoading = false;
      this.trainSuccess = true;
    });
  }
  onUniqueFieldSelect(item: any) {
  }
  onUniqueFieldDeSelect(item: any) {
  }
  onUniqueFieldSelectAll(items: any) {
  }
  onUniqueFieldDeSelectAll(items: any) {
  }
  ngOnDestroy() {
    this.datasetDeleted = false;
    this.datasetEdited = false;
    this.datasetExists = false;
    this.recordsAdded = false;
    this.uploadTrainingSuccess = false;
  }
}