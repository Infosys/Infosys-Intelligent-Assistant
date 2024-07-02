/* Copyright 2022 Infosys Ltd.Use of this source code is governed by MIT license that can be found in the LICENSE file or athttps://opensource.org/licenses/MIT.*/
import { Component, OnInit, ViewChild, ElementRef, OnDestroy, HostListener } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { HttpErrorResponse } from '@angular/common/http';
import { ResourceDetailsComponent } from '../resource-details/resource-details.component';
import { RoasterDetailsComponent } from '../roaster-details/roaster-details.component';
import { MatDialog } from '@angular/material';
import { isNumeric } from 'rxjs/internal/util/isNumeric';
@Component({
  selector: 'app-application-details',
  templateUrl: './application-details.component.html',
  styleUrls: ['./application-details.component.css'],
  providers: [ResourceDetailsComponent, RoasterDetailsComponent]
})
export class ApplicationDetailsComponent implements OnInit {
  @HostListener("window:beforeunload", ["$event"]) beforeUnloadHandler(event: Event) {
    console.log("window:beforeunload");
    event.returnValue = "You will leave this page" as any;
  }
  @HostListener("window:unload", ["$event"]) unloadHandler(event: Event) {
    console.log("window:unload");
  }
  @ViewChild('applicationDetails') fileInput: ElementRef;
  @ViewChild('matDialog') fileInput1: ElementRef;
  noRecords = false;
  hasApplicationDetails: boolean = false;
  confirmValue: boolean = false;
  showUpload: boolean = false;
  deleteAppList: any = [];
  customerId: number = 1;
  chosenTeam: string = "";
  app_lst: any = [];
  teams: any = [];
  loading: boolean = false;
  datasetID: number;
  editRecordId: number = 0;
  editedDocument: any = {};
  maxRecordIdValue: number = 0;
  emptyAssignmentgroup: string = "";
  enableSave = false;
  constructor(private httpService: HttpClient, private dialog: MatDialog, private resourceDetailsObj: ResourceDetailsComponent, private roasterDetialsObj: RoasterDetailsComponent) {
    this.httpService.get('/api/getDatasetTeamNames/' + this.customerId).subscribe(data => {
      if (data['Teams'].length > 0) {
        console.log('data from getdatasetteamnames methode: ' + data['Teams'] + data['DatasetIDs'])
        this.teams = data['Teams'];
        this.httpService.get('/api/getApplicationTeamNames', { responseType: 'text' }).subscribe(team => {
          if (team != 'no team') {
            this.chosenTeam = team;
            this.teamChange();
          }
        });
      } else {
        console.log('No Dataset found!. Create Dataset to proceed with uploading of assignment details');
      }
    }, err => {
      console.log(err);
      throw '';
    });
  }
  ngOnInit() { }
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
  uploadApplicationDetails() {
    // this.saveSuccess=false;
    console.log('in upload application details...')
    const fileBrowser = this.fileInput.nativeElement;
    if (fileBrowser.files && fileBrowser.files[0] && this.chosenTeam != "") {
      this.loading = true;
      const formData = new FormData();
      formData.append('applicationDetails', fileBrowser.files[0]);
      this.httpService.post('/api/uploadApplicationDetails/' + this.customerId + '/' + this.chosenTeam, formData, { responseType: 'text' })
        .subscribe(data => {
          if (data == "success") {
            this.loading = false;
            this.teamChange();
            alert("file uploaded  successfully")
          } else {
            alert("failed to upload")
            this.loading = false;
            console.log('Oops!!, No any data received');
          }
        });
      //this.loading=false;
    } else {
      alert('Please choose the right Team and file..!');
      this.loading = false;
    }
  }
  // ---Edit rows code---
  editApplication(recordId, index) {
    this.editRecordId = recordId;
    this.app_lst[index].prev_app_id = this.app_lst[index].app_id;
    this.app_lst[index].prev_segment_name1 = this.app_lst[index].segment_name1;
    this.app_lst[index].prev_segment_name2 = this.app_lst[index].segment_name2;
    this.app_lst[index].prev_assignment_group = this.app_lst[index].assignment_group;
    this.app_lst[index].prev_sme_flag = this.app_lst[index].sme_flag;
    this.app_lst[index].prev_app_sla = this.app_lst[index].app_sla;
    this.app_lst[index].prev_app_complexity = this.app_lst[index].app_complexity;
    this.app_lst[index].prev_app_weightage = this.app_lst[index].app_weightage;
    this.app_lst[index].prev_service_id = this.app_lst[index].service_id;
    this.app_lst[index].prev_service = this.app_lst[index].service;
    this.app_lst[index].prev_app_infra_id = this.app_lst[index].app_infra_id;
    this.app_lst[index].prev_app_infra = this.app_lst[index].app_infra;
    //this.enableSave = true;
  }
  cancelUpdate() {
    this.editRecordId = 0;
    this.editedDocument = {};
  }
  cancelUpdateNew(index) {
    if (this.app_lst.length == 1) {
      this.hasApplicationDetails = false;
    }
    if (this.app_lst[index].assignment_group === "") {
      //this.app_lst.splice(i, 1);
      this.app_lst.splice(index, 1);
    }
  }
  valueChanged(event, fieldName, rowIndex) {
    if (event.target.outerText) {
      if (fieldName !== 'record_id') {
        this.editedDocument[fieldName] = "";
        this.editedDocument[fieldName] = event.target.outerText;
        this.app_lst[rowIndex][fieldName] = String('');
        this.app_lst[rowIndex][fieldName] = event.target.outerText;
      } else if (fieldName === 'record_id') {
        this.app_lst[rowIndex].temp_application_id = event.target.outerText;
      }
    } else {
      //alert('Invalid value for field ' + fieldName);
    }
  }
  public generateuuid() {
    return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function (c) {
      var r = Math.random() * 16 | 0, v = c == 'x' ? r : (r & 0x3 | 0x8);
      return v.toString(16);
    });
  }
  addNewApplication() {
    const uniqueResId = this.generateuuid();
    let newApp = {
      record_id: 0,
      CustomerID: 1,
      DatasetID: 1,
      app_id: "",
      assignment_group: "",
      app_sla: "",
      sme_flag: "",
      service_id: "",
      service: "",
      app_infra_id: "",
      app_infra: "",
      app_complexity: "",
      app_weightage: "",
      segment_name1: "",
      segment_name2: "Global",
      queue: "",
      temp_application_id: String(uniqueResId)
    };
    this.app_lst.splice(0, 0, newApp);
    this.hasApplicationDetails = true;
    this.noRecords = false;
  }
  updateApplication(customerId, datasetId, recordId, index) {
    var nameFormat = /^[a-zA-Z0-9 _.-]*$/;
    var numberFormat = /^[0-9]{1,3}$/;
    let modified_New_App: any;
    var complexity = ['S', 'C', 'M']
    var smeFlag = ['0', '1'];
    if (this.app_lst[index].app_id.trim() === "") {
      alert("App Id cant be empty");
      return;
    }
    if (!nameFormat.test(String(this.app_lst[index].app_id).toLowerCase())) {
      alert("App Id is invalid");
      return;
    }
    if (this.app_lst[index].segment_name1.trim() === "") {
      alert("Segment Name1  cant be empty");
      return;
    }
    if (this.app_lst[index].segment_name2.trim() === "") {
      alert("Segment Name2  cant be empty");
      return;
    }
    if (this.app_lst[index].assignment_group.trim() === "") {
      alert("Assignment Group cant be empty");
      return;
    }
    if (!nameFormat.test(String(this.app_lst[index].assignment_group).toLowerCase())) {
      alert("Assignment Group is invalid");
      return;
    }
    if (this.app_lst[index].sme_flag.trim() === "") {
      alert("SME Flag value cant be empty");
      return;
    }
    if (!smeFlag.includes(this.app_lst[index].sme_flag.trim())) {
      alert("SME Flag value should 0 or 1");
      return;
    }
    if (this.app_lst[index].app_sla.trim() === "" || this.app_lst[index].app_sla == undefined) {
      alert("App Sla value cant be empty");
      return;
    }
    if (!numberFormat.test(this.app_lst[index].app_sla)) {
      alert("App Sla value should be number");
      return;
    }
    if (this.app_lst[index].app_complexity.trim() === "") {
      alert("App Complexity  value cant be empty");
      return;
    }
    this.app_lst[index].app_complexity = this.app_lst[index].app_complexity.trim().toUpperCase();
    if (!complexity.includes(this.app_lst[index].app_complexity.trim())) {
      alert("App complexity should be S or C or M");
      return;
    }
    if (this.app_lst[index].app_weightage.trim() === "") {
      alert("App Weightage  value cant be empty");
      return;
    }
    if (this.app_lst[index].app_weightage < 0 || this.app_lst[index].app_weightage > 1 || !isNumeric(this.app_lst[index].app_weightage)) {
      alert("App Weightage  value should be between 0 and 1");
      return;
    }
    if (this.app_lst[index].service_id.trim() === "") {
      alert("Service Id cant be empty");
      return;
    }
    if (this.app_lst[index].service.trim() === "") {
      alert("Service cant be empty");
      return;
    }
    if (this.app_lst[index].app_infra_id.trim() === "") {
      alert("App Infra ID cant be empty");
      return;
    }
    if (this.app_lst[index].app_infra.trim() === "") {
      alert("App Infra cant be empty");
      return;
    }
    if (recordId === 0) {
      let Id = parseInt(this.teams.indexOf(this.chosenTeam)) + 1;
      this.app_lst[index].DatasetID = Id;
      this.app_lst[index].record_id = this.app_lst[index].temp_application_id;
      modified_New_App = this.app_lst[index];
    } else {
      modified_New_App = this.app_lst[index];
    }
    if (modified_New_App != undefined) {
      if (modified_New_App.temp_application_id != undefined) {
        delete modified_New_App.temp_application_id;
      }
    }
    this.enableSave = true;
    if (Object.keys(this.editedDocument).length != 0) {
      this.cancelUpdate();
    } else {
      this.cancelUpdate();
    }
  }
  saveApplicationDetails() {
    this.loading = true;
    let data = { "applicationDetails": this.app_lst, "deleteAppList": this.deleteAppList };
    this.httpService
      .post(
        "/api/saveAPplicationDetails",
        //this.app_lst,
        data,
        {
          responseType: "text",
          headers: { "Content-Type": "application/json" },
        }
      )
      .subscribe((updateResponse) => {
        this.loading = false;
        this.enableSave = false;
        if (updateResponse == "success") {
          this.teamChange();
          alert("Updated successfully!");
        } else {
          alert("failed to update!");
        }
      },
        err => {
          console.log(err);
          this.loading = false;
          throw '';
        });
  }
  // -------------------
  deleteApplication(recordId: string, index) {
    this.confirmValue = confirm('Are you sure!, you want to delete this application?');
    if (this.confirmValue) {
      this.enableSave = true;
      this.deleteAppList.push(this.app_lst[index]);
      this.app_lst.splice(index, 1);
    }
  }
  deleteAllApplications() {
    this.confirmValue = confirm('Are you sure!, you want to delete all applications? This will delete all resource details belongs to these applicatons');
    if (this.confirmValue) {
      this.httpService.delete('/api/deleteAllApplications/' + this.customerId + '/' + this.chosenTeam, { responseType: 'text' })
        .subscribe(data => {
          if (data == 'success') {
            // this.saveSuccess=false;
            this.enableSave = false;
            this.teamChange();
            this.resourceDetailsObj.teamChange();
            this.roasterDetialsObj.teamChange();
          } else {
            this.enableSave = false;
            console.log(data);
          }
        });
    }
  }
  canceldelete(index) {
    this.app_lst[index].app_id = this.app_lst[index].prev_app_id;
    this.app_lst[index].segment_name1 = this.app_lst[index].prev_segment_name1;
    this.app_lst[index].segment_name2 = this.app_lst[index].prev_segment_name2;
    this.app_lst[index].assignment_group = this.app_lst[index].prev_assignment_group;
    this.app_lst[index].sme_flag = this.app_lst[index].prev_sme_flag;
    this.app_lst[index].app_sla = this.app_lst[index].prev_app_sla;
    this.app_lst[index].app_complexity = this.app_lst[index].prev_app_complexity;
    this.app_lst[index].app_weightage = this.app_lst[index].prev_app_weightage;
    this.app_lst[index].service_id = this.app_lst[index].prev_service_id;
    this.app_lst[index].service = this.app_lst[index].prev_service;
    this.app_lst[index].app_infra_id = this.app_lst[index].prev_app_infra_id;
    this.app_lst[index].app_infra = this.app_lst[index].prev_app_infra;
    this.cancelUpdate();
    this.enableSave = false;
  }
}
