/* Copyright 2022 Infosys Ltd.Use of this source code is governed by MIT license that can be found in the LICENSE file or athttps://opensource.org/licenses/MIT.*/
import { Component, OnInit, ViewChild, ElementRef, HostListener } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { HttpErrorResponse } from '@angular/common/http';
import { RoasterDetailsComponent } from '../roaster-details/roaster-details.component';
import { Router } from '@angular/router';
import { FormBuilder, FormGroup, FormArray, FormControl, Validators, NgForm } from '@angular/forms';
@Component({
  selector: 'app-resource-details',
  templateUrl: './resource-details.component.html',
  styleUrls: ['./resource-details.component.css'],
  providers: [RoasterDetailsComponent]
})
export class ResourceDetailsComponent implements OnInit {
  @HostListener("window:beforeunload", ["$event"]) beforeUnloadHandler(event: Event) {
    console.log("window:beforeunload");
    event.returnValue = "You will leave this page" as any;
  }
  @HostListener("window:unload", ["$event"]) unloadHandler(event: Event) {
    console.log("window:unload");
  }
  @ViewChild('resourceDetails') fileInput: ElementRef;
  emptyEmailId: string = "";
  enableSave = false;
  hasResourceDetails: boolean = false;
  confirmValue: boolean;
  showUpload: boolean = false;
  resource_lst: any = [];
  deleteResList: any = [];
  customerId: number = 1;
  teams: any = [];
  chosenTeam: string = "";
  loading: boolean = false;
  editResourceId: number = 0;
  editedDocument: any = {};
  maxRecordIdValue: number = 0;
  noRecords = false;
  form: FormGroup;
  QueueData = [
    { name: 'name', value: 'value', selected: false },
    { name: 'name', value: 'value', selected: false },
    { name: 'name', value: 'value', selected: false },
    { name: 'name', value: 'value', selected: false },
    { name: 'name', value: 'value', selected: false }
  ];
  constructor(private httpService: HttpClient, private roasterDetialsObj: RoasterDetailsComponent, private router: Router, private fb: FormBuilder) {
    this.httpService.get('/api/getDatasetTeamNames/' + this.customerId).subscribe(data => {
      if (data['Teams'].length > 0) {
        console.log('data from getdatasetteamnames methode: ' + data['Teams'] + data['DatasetIDs'])
        this.teams = data['Teams'];
        this.httpService.get('/api/getResourceTeamNames', { responseType: 'text' }).subscribe(team => {
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
    this.loading = true;
    this.showUpload = true;
    this.httpService.get('/api/getResourceDetails/' + this.customerId + '/' + this.chosenTeam).subscribe(data => {
      this.loading = false;
      if (Object.keys(data).length != 0) {
        this.resource_lst = data;
        this.hasResourceDetails = true;
      } else {
        this.noRecords = true;
        this.hasResourceDetails = false;
        this.resource_lst = [];
      }
    }, err => {
      console.log(err);
      throw '';
    });
  }
  public generateuuid() {
    return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function (c) {
      var r = Math.random() * 16 | 0, v = c == 'x' ? r : (r & 0x3 | 0x8);
      return v.toString(16);
    });
  }
  addNewResource() {
    const uniqueResId = this.generateuuid();
    let newApp = {
      resource_id: 0,
      resource_name: "",
      email_id: "",
      user_id: "",
      resource_ntid: "",
      CustomerID: 1,
      DatasetID: 1,
      TrainingFlag: 0,
      is_sme: 0,
      res_bandwidth: 100,
      current_workload: 0,
      tickets_assigned: 0,
      shift: [],
      Leave: [],
      queue: [],
      temp_resource_id: String(uniqueResId)
    };
    this.resource_lst.splice(0, 0, newApp);
    this.hasResourceDetails = true;
    this.noRecords = false;
    console.log(this.resource_lst);
  }
  uploadResourceDetails() {
    const fileBrowser = this.fileInput.nativeElement;
    if (fileBrowser.files && fileBrowser.files[0] && this.chosenTeam != "") {
      this.loading = true;
      const formData = new FormData();
      formData.append('resourceDetails', fileBrowser.files[0]);
      this.httpService.post('/api/uploadResourceDetails/' + this.customerId + '/' + this.chosenTeam, formData, { responseType: 'text' })
        .subscribe(data => {
          if (data == "success") {
            this.teamChange();
          } else {
            console.log('Oops!!, data did not came from backend');
          }
        }, err => {
          console.log(err);
          throw '';
        });
      this.loading = false;
    } else {
      alert('Please choose the right Team and file..!');
    }
  }
  saveResourceDetails() {
    let data = { "resourceDetails": this.resource_lst, "deleteResList": this.deleteResList };
    this.loading = true;
    this.httpService
      .post(
        "/api/saveResourceDetails",
        //this.resource_lst,
        data,
        {
          responseType: "text",
          headers: { "Content-Type": "application/json" },
        }
      )
      .subscribe((updateResponse) => {
        this.loading = false;
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
  deleteResource(resourceId: string, rowIndex) {
    console.log("resourceId", resourceId)
    console.log("rowIndex", rowIndex)
    this.confirmValue = confirm('Deleting resource will delete shift details also for the specific resource. Are you sure, you want to delete this resource?');
    this.enableSave = true;
    if (this.confirmValue) {
      let delEmailid = this.resource_lst[rowIndex].email_id;
      if (delEmailid !== undefined) {
        this.deleteResList.push(delEmailid);
      }
      this.resource_lst.splice(rowIndex, 1);
    }
  }
  deleteAllResources() {
    this.confirmValue = confirm('Deleting resource will delete shift details also. Are you sure, you want to delete all resources?');
    if (this.confirmValue) {
      this.httpService.delete('/api/deleteAllResources/' + this.customerId + '/' + this.chosenTeam, { responseType: 'text' })
        .subscribe(data => {
          if (data == 'success') {
            // this.saveSuccess=false;
            this.teamChange();
            this.roasterDetialsObj.teamChange();
          } else {
            console.log(data);
          }
        }, err => {
          console.log(err);
          throw '';
        });
    }
  }
  // ---Edit rows code---
  editResource(resourceId, index, queue) {
    this.editResourceId = resourceId;
    this.resource_lst[index].prev_resource_name = this.resource_lst[index].resource_name;
    this.resource_lst[index].prev_email_id = this.resource_lst[index].email_id;
    this.resource_lst[index].prev_resource_ntid = this.resource_lst[index].resource_ntid;
    this.resource_lst[index].prev_user_id = this.resource_lst[index].user_id;
    // this.enableSave = true;
    this.QueueData = this.QueueData.map(
      (elem) => {
        elem.selected = queue.indexOf(elem.value) != -1 ? true : false;
        return elem
      });
  }
  cancelUpdate() {
    this.editResourceId = 0;
    this.editedDocument = {};
  }
  cancelUpdateNew(i) {
    if (this.resource_lst.length == 1) {
      this.hasResourceDetails = false;
    }
    if (this.resource_lst[i].email_id == "" || this.resource_lst[i].resource_id == "" || this.resource_lst[i].resource_name == "") {
      this.resource_lst.splice(i, 1);
    }
  }
  valueChanged(event, fieldName, rowIndex) {
    if (event.target.outerText) {
      if (fieldName !== 'resource_id') {
        this.editedDocument[fieldName] = event.target.outerText;
        this.resource_lst[rowIndex][fieldName] = event.target.outerText;
        console.log('editdocument is: ' + this.editedDocument[fieldName]);
      } else if (fieldName === 'resource_id') {
        this.resource_lst[rowIndex].temp_resource_id = event.target.outerText;
      }
    } else {
    }
  }
  editResourceLeave(resourceId, emailId: string, resourceName: string) {
    this.router.navigate(['/shiftdetails', this.customerId, this.chosenTeam, emailId, resourceName]);
  }
  updateResource(customerId, datasetId, resourceId, index) {
    const regularExpression = /^(([^<>()\[\]\\.,;:\s@"]+(\.[^<>()\[\]\\.,;:\s@"]+)*)|(".+"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/;
    let modified_New_Res: any;
    var nameFormat = /^[a-zA-Z0-9 _.-]*$/;
    this.resource_lst[index].resource_name = this.resource_lst[index].resource_name.trim();
    this.resource_lst[index].email_id = this.resource_lst[index].email_id.trim();
    if (this.resource_lst[index].resource_name.trim() === "") {
      alert("Resource Name cant be empty");
      return;
    }
    if (!nameFormat.test(String(this.resource_lst[index].resource_name).toLowerCase())) {
      alert("Resource Name is invalid");
      return;
    }
    if (this.resource_lst[index].email_id.trim() === "") {
      alert("Email Id cant be empty");
      return;
    }
    if (!regularExpression.test(String(this.resource_lst[index].email_id).toLowerCase())) {
      alert("Email Id is invalid");
      return;
    }
    if (this.resource_lst[index].resource_ntid.trim() === "") {
      alert("Resource ntid cant be empty");
      return;
    }
    if (this.resource_lst[index].user_id.trim() === "") {
      alert("User ID cant be empty");
      return;
    }
    if (resourceId === 0) {
      let Id = parseInt(this.teams.indexOf(this.chosenTeam)) + 1;
      this.resource_lst[index].DatasetID = Id;
      this.resource_lst[index].resource_id = this.resource_lst[index].temp_resource_id;
      modified_New_Res = this.resource_lst[index];
    } else {
      modified_New_Res = this.resource_lst[index];
    }
    alert("Successfully Updated.")
    if (modified_New_Res != undefined) {
      if (modified_New_Res.temp_resource_id != undefined) {
        delete modified_New_Res.temp_resource_id;
      }
    }
    this.cancelUpdate();
    this.enableSave = true;
    if (Object.keys(this.editedDocument).length != 0) {
      this.cancelUpdate();
    }
  }
  // -------------------
  canceldelete(index) {
    this.resource_lst[index].resource_name = this.resource_lst[index].prev_resource_name;
    this.resource_lst[index].email_id = this.resource_lst[index].prev_email_id;
    this.resource_lst[index].resource_ntid = this.resource_lst[index].prev_resource_ntid;
    this.resource_lst[index].user_id = this.resource_lst[index].prev_user_id;
    this.cancelUpdate();
    this.enableSave = false;
  }
  onCheckboxChange($event, resourceName) {
    // this.editResourceId = resourceId;
    if ($event.target.checked) {
      for (let item of this.resource_lst) {
        if (item["resource_name"] === resourceName) {
          item.queue = (typeof item.queue != 'undefined' && item.queue instanceof Array) ? item.queue : []
          item.queue.push($event.target.value)
        }
      }
    } else {
      let i: number = 0;
      this.QueueData.forEach((item) => {
        if (item.value == $event.target.value) {
          for (let item of this.resource_lst) {
            if (item["resource_name"] === resourceName) {
              const index: number = item.queue.indexOf($event.target.value);
              if (index !== -1) {
                item.queue.splice(index, 1);
              }
            }
          }
          return;
        }
        i++;
      });
    }
  }
  submitForm() {
  }
}
