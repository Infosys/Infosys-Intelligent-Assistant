/* Copyright 2022 Infosys Ltd.Use of this source code is governed by MIT license that can be found in the LICENSE file or athttps://opensource.org/licenses/MIT.*/
import { Component, OnInit, ViewChild, ElementRef, HostListener } from "@angular/core";
import { HttpClient } from "@angular/common/http";
import { HttpErrorResponse } from "@angular/common/http";
import { ResourceDetailsComponent } from "../resource-details/resource-details.component";
import { RoasterDetailsComponent } from "../roaster-details/roaster-details.component";
import { MatSelect } from "@angular/material/select";
import { MatDialog } from "@angular/material";
import { isUndefined } from "util";
import { MatDatepicker, MatDatepickerInputEvent } from '@angular/material/datepicker';
import { Router } from '@angular/router';
import { NgbModal, NgbActiveModal, ModalDismissReasons } from '@ng-bootstrap/ng-bootstrap';
import { ValidationMessageComponent } from '../validation-message/validation-message.component'
declare var $: any;
@Component({
  selector: "app-mapping-details",
  templateUrl: "./mapping_details.component.html",
  styleUrls: ["./mapping_details.component.css"],
  providers: [ResourceDetailsComponent, RoasterDetailsComponent],
})
export class MappingDetailsComponent implements OnInit {
  noRecords = false;
  teamId = [];
  @HostListener("window:beforeunload", ["$event"]) beforeUnloadHandler(event: Event) {
    console.log("window:beforeunload");
    event.returnValue = "You will leave this page" as any;
  }
  @HostListener("window:unload", ["$event"]) unloadHandler(event: Event) {
    console.log("window:unload");
  }
  @ViewChild("applicationDetails") fileInput: ElementRef;
  @ViewChild("matDialog") fileInput1: ElementRef;
  @ViewChild("singleSelect") singleSelect: MatSelect;
  //@ViewChild('roasterDetails') fileInput2:ElementRef;
  public CLOSE_ON_SELECTED = false;
  public init = new Date();
  public resetModel = new Date(0);
  public model = [
    new Date('7/15/1966'),
    new Date('3/23/1968'),
    new Date('7/4/1992'),
    new Date('1/25/1994'),
    new Date('6/17/1998')
  ];
  @ViewChild('picker') _picker: MatDatepicker<Date>;
  //@ViewChildren('picker') _picker: QueryList<MatDatepicker<Date>>;
  showShiftDetails: boolean = false;
  hasRoasterDetails: boolean = false;
  //showUpload1: boolean = false;
  roasterAlert: boolean;
  loader: boolean;
  roasterResourceDetails: any = [];
  teams1: any = [];
  resourceName: string = "";
  //customerId1: number = 1;
  chosenTeam1: string = "All";
  confirmValue1: boolean;
  failedRoasterData: any = [];
  emailId: string;
  message: string;
  sampleArray: any =
    [
      { "id": 0, "model": [new Date('7/15/1966'), new Date('7/15/1967')] },
      { "id": 1, "model": [new Date('7/15/1998'), new Date('7/15/1999')] }
    ];
  rowSelectedinTable: any = 0;
  hasApplicationDetails: boolean = false;
  confirmValue: boolean = false;
  showUpload: boolean = false;
  backupResources: any;
  customerId: number = 1;
  chosenTeam: string = "";
  resources = ["resource1", "resource2", "resource3", "resource4", "resource5", "resource6"];
  applications: Array<string> = ["test", "Test", "Test", "Test"];
  // backupApplications: Array<string> = ["test", "Test", "Test", "Test"];
  backupApplications: any;
  shifts = ["F", "S", "H"];
  application = [];
  resource = "All";
  new_row: boolean;
  app_lst: any = [
    {
      email_id: "email",
      resource_id: "1",
      resource_name: "name",
      resource_shift: "F",
      resource_W1: "Sat",
      resource_W2: "Sun",
      resource_group: ["test"],
      start_date: new Date("06/02/2021"),
      end_date: new Date("06/08/2021"),
      _id: { $oid: "5d6df9296ba0c77648f921b2" },
    },
  ];
  teams: any = [];
  loading: boolean = false;
  editRecordId: number = 0;
  editedDocument: any = {};
  backup_app_lst: any;
  appresourceMappingDetails: any = [];
  resourceNamesData: any = [];
  applicationsData: any = [];
  searchGroup: any = "";
  constructor(
    private httpService: HttpClient,
    private dialog: MatDialog,
    private resourceDetailsObj: ResourceDetailsComponent,
    private roasterDetialsObj: RoasterDetailsComponent,
    private router: Router,
    private modalService: NgbModal
  ) {
  }
  ngOnInit() {
    this.httpService.get('/api/getDatasetTeamNames/' + this.customerId).subscribe(data => {
      if (data['Teams'].length > 0) {
        console.log('data from getdatasetteamnames methode: ' + data['Teams'] + data['DatasetIDs'])
        this.teams1 = data['Teams'];
        this.httpService.get('/api/getRoasterTeamNames', { responseType: 'text' }).subscribe(team => {
          if (team != 'no team') {
            this.chosenTeam1 = team;
            this.loading = true;
            this.getResourceApplicationDetails();
            this.httpService.get('/api/applicationResourceMapping')
              .subscribe(data => {
                this.loading = false;
                this.appresourceMappingDetails = data;
                this.backup_app_lst = data;
                console.log("applicationResourceMapping", data);
                this.searchTeam(this.chosenTeam1);
              },
                err => {
                  console.log(err);
                  throw "";
                });
            // this.teamChange1();
          } else {
            this.hasApplicationDetails = false;
          }
        });
      } else {
        this.hasApplicationDetails = false;
        console.log('No Dataset found!. Create Dataset to proceed with uploading of assignment details');
      }
    }, err => {
      console.log(err);
      throw '';
    });
    this.backup_app_lst = this.app_lst.slice();
  }
  teamChange() {
    this.showUpload = true;
    this.httpService
      .get(
        "/api/getApplicationDetails/" + this.customerId + "/" + this.chosenTeam1
      )
      .subscribe(
        (data) => {
          if (Object.keys(data).length != 0) {
            //this.app_lst = data;
            this.hasApplicationDetails = false;
          } else {
            this.hasApplicationDetails = true;
            this.app_lst = [];
          }
        },
        (err) => {
          console.log(err);
          throw "";
        }
      );
  }
  public dateClass = (date: Date) => {
    if (this._findDate(date) !== -1) {
      return ['selected'];
    }
    return [];
  }
  public datePickerRow(rowIndex: any) {
    this.rowSelectedinTable = rowIndex;
  }
  public dateChanged(event: MatDatepickerInputEvent<Date>, rowIndex): void {
    if (event.value) {
      const date = event.value;
      const index = this._findDate(date);
      if (index === -1) {
        //this.model.push(date);
        this.sampleArray[rowIndex].model.push(date);
      } else {
        //this.model.splice(index, 1);
        this.sampleArray[rowIndex].model.splice(index, 1);
      }
      //this.resetModel = new Date(0);
      if (!this.CLOSE_ON_SELECTED) {
        const closeFn = this._picker.close;
        this._picker.close = () => { };
        this._picker['_popupComponentRef'].instance._calendar.monthView._createWeekCells()
        setTimeout(() => {
          this._picker.close = closeFn;
        });
      }
    }
  }
  public remove(date: Date): void {
    const index = this._findDate(date);
    this.model.splice(index, 1)
  }
  private _findDate(date: Date): number {
    const rowIndex = this.rowSelectedinTable;
    return this.sampleArray[rowIndex].model.map((m) => +m).indexOf(+date);
  }
  openValidationMessageModal() {
    const modalRef = this.modalService.open(ValidationMessageComponent, { ariaLabelledBy: 'modal-basic-title', size: "lg" });
    modalRef.componentInstance.failedRoasterUploadDetails = this.failedRoasterData;
  }
  getlatestDataPostSave() {
    this.backup_app_lst = this.app_lst.slice();
    this.hasApplicationDetails = false;
    this.httpService.get('/api/applicationResourceMapping')
      .subscribe(data => {
        this.appresourceMappingDetails = data;
        this.backup_app_lst = data;
        console.log(data);
      },
        err => {
          console.log(err);
          throw "";
        });
    this.getResourceApplicationDetails();
  }
  uploadApplicationDetails() {
    const fileBrowser = this.fileInput.nativeElement;
    if (fileBrowser.files && fileBrowser.files[0] && this.chosenTeam != "") {
      this.loading = true;
      const formData = new FormData();
      formData.append("applicationDetails", fileBrowser.files[0]);
      this.httpService
        .post(
          "/api/uploadApplicationDetails/" +
          this.customerId +
          "/" +
          this.chosenTeam,
          formData,
          { responseType: "text" }
        )
        .subscribe((data) => {
          if (data == "success") {
            this.loading = false;
            this.teamChange();
          } else {
            console.log("Oops!!, No any data received");
          }
        });
      this.loading = false;
    } else {
      alert("Please choose the right Team and file..!");
    }
  }
  // ---Edit rows code---
  editApplication(recordId) {
    this.editRecordId = recordId;
    //   this.dropdownSettings.disabled = false;
  }
  cancelUpdate(i) {
    if (this.appresourceMappingDetails[i].resource_id !== 0) {
      this.editRecordId = 0;
      this.editedDocument = {};
    } else {
      this.app_lst.splice(i, 1);
      this.appresourceMappingDetails.splice(i, 1);
    }
  }
  valueChanged(event, fieldName) {
    console.log(
      "new value is: " + event.target.outerText + ", field name: " + fieldName
    );
    console.log(
      "record id is added successfully: ",
      this.editedDocument["resource_id"]
    );
    if (event.target.outerText) {
      this.editedDocument[fieldName] = event.target.outerText;
      console.log("editdocument is: " + this.editedDocument[fieldName]);
    } else {
      alert("Invalid value for field " + fieldName);
    }
  }
  updateApplication(recordId, index) {
    this.teamId = [];
    if (this.chosenTeam1 == 'All') {
      this.teams1.forEach((index) => {
        var val1 = this.getKeyByValue(this.teams1, index);
        this.teamId.push(parseInt(val1) + 1);
      })
    } else {
      var val1 = this.getKeyByValue(this.teams1, this.chosenTeam1);
      this.teamId.push(parseInt(val1) + 1);
    }
    let modified_New_resource: any;
    if (recordId === 0) {
      this.appresourceMappingDetails[index].DatasetID = this.teamId;
      this.appresourceMappingDetails[index].resource_id = this.appresourceMappingDetails[index].temp_resource_id;
      modified_New_resource = this.appresourceMappingDetails[index];
    } else {
      modified_New_resource = this.appresourceMappingDetails[index];
    }
    //if (Object.keys(this.editedDocument).length != 0) {
    if (modified_New_resource != undefined) {
      if (modified_New_resource.temp_resource_id != undefined) {
        delete modified_New_resource.temp_resource_id;
      }
      //new start
      var dt = new Date();
      var month = dt.getMonth() + 1
      var year = dt.getFullYear();
      const daysInMonth = new Date(year, month, 0).getDate();
      this.loading = true;
      this.httpService
        .put(
          "/api/updateApplication/" + daysInMonth,
          modified_New_resource,
          //new end
          {
            responseType: "text",
            headers: { "Content-Type": "application/json" },
          }
        )
        .subscribe((updateResponse) => {
          this.loading = false;
          if (updateResponse == "success") {
            this.getlatestDataPostSave();
            alert("Updated successfully!");
            this.cancelUpdate(index);
            this.teamChange();
          } else {
            alert("failed to update!");
          }
        },
          err => {
            this.getlatestDataPostSave();
            console.log(err);
            this.loading = false;
            throw '';
          });
      this.cancelUpdate(index);
      this.teamChange();
    } else {
      alert("Nothing to update!");
      this.cancelUpdate(index);
    }
  }
  // -------------------
  deleteApplication(recordId: string, index) {
    this.confirmValue = confirm(
      "Are you sure!, you want to delete this application?"
    );
    if (this.confirmValue) {
      //alert(recordId) ;      
      this.appresourceMappingDetails.splice(index, 1);
      this.httpService
        .delete(
          "/api/deleteAnalystMapping/" + this.customerId + "/" + this.chosenTeam1 + "/" +
          recordId,
          { responseType: "text" }
        )
        .subscribe((data) => {
          if (data == "success") {
            this.teamChange();
            this.resourceDetailsObj.teamChange();
            this.roasterDetialsObj.teamChange();
          } else {
            console.log(data);
          }
        });
    }
  }
  deleteAllApplications() {
    this.confirmValue = confirm(
      "Are you sure!, you want to delete all applications? This will delete all resource details belongs to these applicatons"
    );
    if (this.confirmValue) {
      this.httpService
        .delete(
          "/api/deleteAllApplications/" +
          this.customerId +
          "/" +
          this.chosenTeam,
          { responseType: "text" }
        )
        .subscribe((data) => {
          if (data == "success") {
            // this.saveSuccess=false;
            this.teamChange();
            this.resourceDetailsObj.teamChange();
            this.roasterDetialsObj.teamChange();
          } else {
            console.log(data);
          }
        });
    }
  }
  deleteAllResourcesMapping() {
    this.confirmValue = confirm('Deleting resource mapping will delete shift details and shift mapping also. Are you sure, you want to delete all resources mapping?');
    if (this.confirmValue) {
      this.httpService.delete('/api/deleteAllAnalystMapping/' + this.customerId + "/" + this.chosenTeam1, { responseType: 'text' })
        .subscribe(data => {
          if (data == 'success') {
            this.ngOnInit();
          } else {
            console.log(data);
          }
        }, err => {
          console.log(err);
          throw '';
        });
    }
  }
  getResourceApplicationDetails() {
    this.httpService.get('/api/getResourceDetails/' + this.customerId + "/" + this.chosenTeam1)
      .subscribe(data => {
        this.resourceNamesData = data;
        this.backupResources = data;
        console.log(data);
      },
        err => {
          console.log(err);
          throw "";
        });
    this.httpService.get('/api/getApplicationsForTeam/' + this.customerId + "/" + this.chosenTeam1)
      .subscribe(data => {
        this.applicationsData = data;
        this.backupApplications = data;
        console.log(data);
      },
        err => {
          console.log(err);
          throw "";
        });
  }
  searchTeam($event) {
    this.getResourceApplicationDetails();
    this.resource = 'All';
    this.teamId = [];
    if ($event == 'All') {
      this.teams1.forEach((index) => {
        var val1 = this.getKeyByValue(this.teams1, index);
        this.teamId.push(parseInt(val1) + 1);
      })
    } else {
      var val1 = this.getKeyByValue(this.teams1, $event);
      this.teamId.push(parseInt(val1) + 1);
    }
    if (this.teamId !== [] && this.teamId.length !== 0) {
      let new_list = this.backup_app_lst.slice();
      this.appresourceMappingDetails = new_list.filter((val) => {
        if (
          this.checkApplication(this.teamId, val.DatasetID)
        ) {
          return val;
        }
        console.log(this.appresourceMappingDetails)
      });
      this.noRecords = false;
      if (this.appresourceMappingDetails.length == 0) {
        this.noRecords = true;
      }
      console.log(this.appresourceMappingDetails);
    } else if (this.teamId !== [] && this.teamId.length !== 0) {
      console.log(this.app_lst);
      let new_list = this.backup_app_lst.slice();
      this.appresourceMappingDetails = new_list.filter((val) => {
        if (this.checkApplication(this.teamId, val.DatasetID)) {
          return val;
        }
        console.log(this.appresourceMappingDetails)
      });
      this.noRecords = false;
      if (this.appresourceMappingDetails.length == 0) {
        this.noRecords = true;
      }
      console.log(this.app_lst);
    } else {
      //this.appresourceMappingDetails = this.backup_app_lst;
      //this.applicationsData = this.backupApplications.slice();
    }
    console.log(this.app_lst);
  }
  searchResource($event) {
    console.log($event);
    this.resource = $event;
    console.log(this.resource);
    if (this.resource !== "All" && this.application.length != 0) {
      let new_list = this.backup_app_lst.slice();
      this.appresourceMappingDetails = new_list.filter((val) => {
        if (
          val.resource_name.toLowerCase() == this.resource.toLowerCase() &&
          this.checkApplication(this.application, val.resource_group) && this.checkApplication(this.teamId, val.DatasetID)
        ) {
          return val;
        }
      });
      console.log(this.appresourceMappingDetails);
    } else if (this.resource !== "All" && this.application.length == 0) {
      let new_list = this.backup_app_lst.slice();
      this.appresourceMappingDetails = new_list.filter(
        (val) => {
          if (val.resource_name.toLowerCase() == this.resource.toLowerCase() && this.checkApplication(this.teamId, val.DatasetID)) {
            return val;
          }
        });
      console.log(this.appresourceMappingDetails);
    } else if (this.resource == "All" && this.application.length !== 0) {
      let new_list = this.backup_app_lst.slice();
      this.appresourceMappingDetails = new_list.filter((val) => {
        if (
          this.checkApplication(this.application, val.resource_group) && this.checkApplication(this.teamId, val.DatasetID)
        ) {
          return val;
        }
      });
      console.log(this.appresourceMappingDetails);
    } else if (this.resource == "All" && this.application.length == 0) {
      let new_list = this.backup_app_lst.slice();
      this.appresourceMappingDetails = new_list.filter((val) => {
        if (
          this.checkApplication(this.teamId, val.DatasetID)
        ) {
          return val;
        }
      });
      console.log(this.appresourceMappingDetails);
    } else {
      this.appresourceMappingDetails = this.backup_app_lst;
    }
  }
  searchApplication($event) {
    console.log($event);
    let applicationsData1 = $event;
    console.log(this.application);
    if (applicationsData1 !== [] && applicationsData1.length !== 0 && this.resource !== "All") {
      let new_list = this.backup_app_lst.slice();
      this.appresourceMappingDetails = new_list.filter((val) => {
        if (
          val.resource_name.toLowerCase() == this.resource.toLowerCase() && this.checkApplication(applicationsData1, val.resource_group) && this.checkApplication(this.teamId, val.DatasetID)
        ) {
          return val;
        }
      });
      console.log(this.app_lst);
    } else if (applicationsData1.length == 0 && this.resource !== "All") {
      console.log(this.app_lst);
      let new_list = this.backup_app_lst.slice();
      this.appresourceMappingDetails = new_list.filter((val) => {
        if (val.resource_name.toLowerCase() == this.resource.toLowerCase() && this.checkApplication(this.teamId, val.DatasetID)) {
          return val;
        }
      });
      console.log(this.app_lst);
    }
    else if (applicationsData1.length !== 0 && this.resource == "All") {
      let new_list = this.backup_app_lst.slice();
      this.appresourceMappingDetails = new_list.filter((val) => {
        if (
          this.checkApplication(applicationsData1, val.resource_group) && this.checkApplication(this.teamId, val.DatasetID)
        ) {
          return val;
        }
      });
      console.log(this.app_lst);
    }
    else if (applicationsData1.length == 0 && this.resource == "All") {
      let new_list = this.backup_app_lst.slice();
      this.appresourceMappingDetails = new_list.filter((val) => {
        if (
          this.checkApplication(this.teamId, val.DatasetID)
        ) {
          return val;
        }
      });
      console.log(this.app_lst);
    } else {
      this.appresourceMappingDetails = this.backup_app_lst;
      this.applicationsData = this.backupApplications.slice();
    }
    console.log(this.app_lst);
  }
  checkApplication(a, b) {
    console.log(a, b);
    let count = 0;
    for (let i = 0; i < a.length; i++) {
      if (b.indexOf(a[i]) === -1) {
        count = count + 1;
        //return false;
      } else {
        console.log("found a match for selected application..." + a[i]);
      }
    }
    if (count === a.length) {
      return false;
    }
    return true;
  }
  addNewResource() {
    let newres = {
      resource_id: 0,
      resource_name: null,
      resource_group: [],
      temp_resource_id: 0
    };
    this.app_lst.splice(0, 0, newres);
    this.appresourceMappingDetails.splice(0, 0, newres);
  }
  resourceChange($event, resoure_id) {
    if (resoure_id === 0) {
      let index = this.appresourceMappingDetails.findIndex(i => i.resource_id === resoure_id);
      this.appresourceMappingDetails[index].resource_name = $event;
      console.log(this.appresourceMappingDetails);
    }
    console.log(this.backup_app_lst);
    if (
      this.backup_app_lst.filter((val) => val.resource_name === $event && val.resource_id !== 0)
        .length !== 0
    ) {
      console.log(this.backup_app_lst);
      alert("User Already Exist");
    }
  }
  resourceSSelected(name, id, rowindex) {
    //let index = this.appresourceMappingDetails.findIndex(i => i.resource_id == id);
    this.appresourceMappingDetails[rowindex].resource_name = name;
    this.appresourceMappingDetails[rowindex].temp_resource_id = id;
    console.log(this.appresourceMappingDetails);
  }
  applicationSelect($event, rowindex) {
    this.appresourceMappingDetails[rowindex].resource_group = $event;
    console.log(this.appresourceMappingDetails);
  }
  findGroup($event) {
    if ($event !== "") {
      this.applications = this.backupApplications.slice();
      let app_name = $event;
      this.applicationsData = this.applicationsData.filter((val) =>
        val.toLowerCase().includes(app_name.toLowerCase())
      );
    } else {
      this.applicationsData = this.backupApplications.slice();
    }
    console.log(this.applications);
  }
  findResource($event) {
    if ($event !== "") {
      this.resourceNamesData = this.backupResources.slice();
      let res_name = String($event);
      this.resourceNamesData = this.resourceNamesData.filter(i => i.resource_name.toLowerCase().includes(res_name.toLowerCase()));
    } else {
      this.resourceNamesData = this.backupResources.slice();
    }
  }
  clearSearch(value) {
    if (value === "Group") {
      this.searchGroup = "";
      this.applicationsData = this.backupApplications.slice();
    }
    if (value === "User") {
      this.searchGroup = "";
      this.resourceNamesData = this.backupResources.slice();
    }
  }
  getKeyByValue(object, value) {
    return Object.keys(object).find(key => object[key] === value);
  }
}
