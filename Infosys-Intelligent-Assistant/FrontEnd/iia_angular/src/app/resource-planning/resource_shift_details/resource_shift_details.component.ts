/* Copyright 2022 Infosys Ltd.Use of this source code is governed by MIT license that can be found in the LICENSE file or athttps://opensource.org/licenses/MIT.*/
import { Component, OnInit, ViewChild, ElementRef, ViewEncapsulation, HostListener } from "@angular/core";
import { HttpClient } from "@angular/common/http";
import { HttpErrorResponse } from "@angular/common/http";
import { ResourceDetailsComponent } from "../resource-details/resource-details.component";
import { RoasterDetailsComponent } from "../roaster-details/roaster-details.component";
import { MatDialog } from "@angular/material";
import { DatePipe } from '@angular/common';
import { Pipe, PipeTransform } from "@angular/core";
import * as moment from 'moment';
import { MatDatepicker, MatDatepickerInputEvent } from '@angular/material/datepicker';
import { NgbModal, NgbActiveModal, ModalDismissReasons } from '@ng-bootstrap/ng-bootstrap';
import { ValidationMessageComponent } from '../validation-message/validation-message.component'
import { MatTableDataSource, MatPaginator, MatSort, MatPaginatorModule, MatTableModule } from '@angular/material';
import { C, E } from "@angular/cdk/keycodes";
import { THIS_EXPR } from "@angular/compiler/src/output/output_ast";
@Component({
  selector: "app-resourceShiftDetails-details",
  templateUrl: "./resource_shift_details.component.html",
  styleUrls: ["./resource_shift_details.component.css"],
  providers: [ResourceDetailsComponent, RoasterDetailsComponent, DatePipe],
  encapsulation: ViewEncapsulation.None
})
export class ResourceShiftDetailsComponent implements OnInit {
  isValidDate: any;
  enableSave = false;
  error: { isError: boolean; errorMessage: string; };
  todayDate: Date;
  @ViewChild(MatPaginator) paginator: MatPaginator;
  dataSetId: number;
  dataSource: any;
  @HostListener("window:beforeunload", ["$event"]) beforeUnloadHandler(event: Event) {
    console.log("window:beforeunload");
    event.returnValue = "You will leave this page" as any;
  }
  @HostListener("window:unload", ["$event"]) unloadHandler(event: Event) {
    console.log("window:unload");
  }
  @ViewChild('roasterDetails') fileInput2: ElementRef;
  test: string = "";
  noOfRoasterMapping
  itemsPerPage: number = 10;
  page: number = 1;
  pageSize = 10;
  showUpload1: boolean = false;
  teams1: any = [];
  customerId1: number = 1;
  chosenTeam1: string = "";
  confirmValue1: boolean;
  message: string;
  roasterAlert: boolean;
  roasterResourceDetails: any = [];
  hasRoasterDetails: boolean = false;
  loader: boolean;
  failedRoasterData: any = [];
  deleteRosterList: any = [];
  daysSelected: any[] = [];
  event: any;
  selectedDate: any;
  highlightDays: any[];
  initialCount: Array<any>; // this is the [(ngModel)] property
  datesArray: Array<any>;
  myMonth: any;
  modified_resource: any = [];
  selectedRes = 'All';
  testItems: any[] = [
    { 'item': 'array1', 'id': 1 },
    { 'item': 'array2', 'id': 2 },
    { 'item': 'array3', 'id': 3 },
  ]  // potential use if person wanted to create a choosen item to associate with a list of arrays
  public CLOSE_ON_SELECTED = false;
  public init = new Date();
  public resetModel = new Date(0);
  public model = [];
  rowSelectedinTable: any = 0;
  @ViewChild('picker') _picker: MatDatepicker<Date>;
  tableView: boolean = true;
  hasApplicationDetails: boolean = false;
  confirmValue: boolean = false;
  showUpload: boolean = false;
  searchGroup: any = "";
  customerId: number = 1;
  chosenTeam: string = "";
  resources: any;
  resource = "All";
  backupResources: any;
  cloneResourceRecord: any;
  public months: Array<any> = [
    { _id: 1, month: "January", days: 31 },
    { _id: 2, month: "February", days: 28 },
    { _id: 3, month: "March", days: 31 },
    { _id: 4, month: "April", days: 30 },
    { _id: 5, month: "May", days: 31 },
    { _id: 6, month: "June", days: 30 },
    { _id: 7, month: "July", days: 31 },
    { _id: 8, month: "August", days: 31 },
    { _id: 9, month: "September", days: 30 },
    { _id: 10, month: "October", days: 31 },
    { _id: 11, month: "November", days: 30 },
    { _id: 12, month: "December", days: 31 },
  ];
  selected_Month_id: number = 0;
  days_in_selected_month = 0;
  selected_Month: string = "";
  group = ["AS1", "AS2", "AS3", "AS4"];
  shifts: any;//= ["F", "S", "H"];
  app_lst: any = [];
  res_shift_lst: any = [];
  modified_records_list: any = [];
  backup_app_lst: any = [];
  length_of_list: number = 0;
  monthNamSelected: String = "";
  monthNames = [
    'January',
    'February',
    'March',
    'April',
    'May',
    'June',
    'July',
    'August',
    'September',
    'October',
    'November',
    'December'
  ];
  teams: any = [];
  loading: boolean = false;
  editRecordId: number = -1;
  editedDocument: any = {};
  gridView: boolean = false;
  constructor(
    private httpService: HttpClient,
    private dialog: MatDialog,
    private resourceDetailsObj: ResourceDetailsComponent,
    private roasterDetialsObj: RoasterDetailsComponent,
    private datePipe: DatePipe,
    private modalService: NgbModal
  ) {
    this.httpService.get('/api/getDatasetTeamNames/' + this.customerId).subscribe(data => {
      if (data['Teams'].length > 0) {
        console.log('data from getdatasetteamnames methode: ' + data['Teams'] + data['DatasetIDs'])
        this.teams1 = data['Teams'];
        this.httpService.get('/api/getRoasterTeamNames', { responseType: 'text' }).subscribe(team => {
          if (team != 'no team') {
            this.chosenTeam1 = team;
            this.teamChange1();
            console.log("resource_shift")
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
  ngOnInit() {
  }
  private getRoasterMappingCount() {
    this.httpService.get('/api/getRoasterMappingCount/' + this.customerId + '/' + this.chosenTeam1 + '/' + this.selectedRes + '/' + this.monthNamSelected).subscribe(data => {
      console.log('in getPredictedTickets');
      this.noOfRoasterMapping = data['count'];
      console.log("noOfRoasterMapping", this.noOfRoasterMapping)
      this.itemsPerPage = 10;
      this.pageChanged();
    });
  }
  getlatestDataPostSave() {
    this.getMonthName_days_of_month(new Date().getMonth() + 1);
    var dt = new Date();
    var month = dt.getMonth() + 1;
    var year = dt.getFullYear();
    const daysInMonth = new Date(year, month, 0).getDate();
    // this.httpService.get('/api/getRosterScreenMappingDetails/'+ daysInMonth)
    this.httpService.get('/api/getRosterScreenMappingDetails/' + this.customerId + '/' + this.chosenTeam1 + '/' + this.days_in_selected_month + '/' + this.selectedRes + '/' + this.monthNamSelected + '/' + this.itemsPerPage + '/' + this.page)
      .subscribe(data => {
        this.app_lst = data;
        this.backup_app_lst = data;
        console.log(data);
        this.app_lst.map(v => Object.assign(v, { modified: false }));
        this.backup_app_lst.map(v => Object.assign(v, { modified: false }));
      },
        err => {
          console.log(err);
          throw "";
        });
    this.httpService.get('/api/getRosterScreenMappingDetails1/' + daysInMonth)
      .subscribe(data => {
        this.res_shift_lst = data;
        this.backup_app_lst = data;
      },
        err => {
          console.log(err);
          throw "";
        });
    this.getResourceApplicationDetails();
    this.httpService.get('/api/getRosterUniqueShifts')
      .subscribe(data => {
        this.shifts = data;
        console.log(data);
      },
        err => {
          console.log(err);
          throw "";
        });
  }
  getResourceApplicationDetails() {
    this.httpService.get('/api/getResourceDetails/' + this.customerId + "/" + this.chosenTeam1)
      .subscribe(data => {
        this.resources = data;
        console.log("resources data", this.resources)
        this.backupResources = data;
        console.log(data);
      },
        err => {
          console.log(err);
          throw "";
        });
  }
  pageChanged() {
    this.loader = true;
    //this.getMonthName_days_of_month(new Date().getMonth() + 1);
    var dt = new Date();
    var month = dt.getMonth() + 1;
    var year = dt.getFullYear();
    const daysInMonth = new Date(year, month, 0).getDate();
    this.httpService.get('/api/getRosterScreenMappingDetails/' + this.customerId + '/' + this.chosenTeam1 + '/' + this.days_in_selected_month + '/' + this.selectedRes + '/' + this.monthNamSelected + '/' + this.itemsPerPage + '/' + this.page)
      .subscribe(data => {
        this.app_lst = data;
        this.backup_app_lst = data;
        console.log("Inside pageChanged() app_list value ", this.app_lst)
        this.loader = false;
        this.app_lst.map(v => Object.assign(v, { modified: false }));
        this.backup_app_lst.map(v => Object.assign(v, { modified: false }));
      }
      )
    // alert(this.monthNamSelected);
  }
  isSelected = (event: any) => {
    const date = event.year() + "-" + event.month() + "-" + event.date();
    return this.daysSelected.find(x => x == date) ? "selected" : null;
  };
  select(event: any, calendar: any) {
    const date = event.year() + "-" + event.month() + "-" + event.date();
    const index = this.daysSelected.findIndex(x => x == date);
    if (index < 0) this.daysSelected.push(date);
    else this.daysSelected.splice(index, 1);
  }
  addRoster() {
    let newRoster = {
      resource_id: 0,
      resource_name: null,
      resource_group: [],
      temp_resource_id: 0,
      email_id: null,
      list_shift: [],
      weekoff: [],
    };
    this.resetModel = new Date(0);
    this.app_lst.splice(0, 0, newRoster);
  }
  teamChange() {
    this.showUpload = true;
    this.httpService
      .get(
        "/api/getApplicationDetails/" + this.customerId + "/" + this.chosenTeam
      )
      .subscribe(
        (data) => {
          if (Object.keys(data).length != 0) {
          } else {
            this.app_lst = [];
          }
        },
        (err) => {
          console.log(err);
          throw "";
        }
      );
  }
  teamChange1() {
    var val1 = this.getKeyByValue(this.teams1, this.chosenTeam1);
    this.dataSetId = parseInt(val1) + 1
    this.getMonthName_days_of_month(new Date().getMonth() + 1);
    var dt = new Date();
    var month = dt.getMonth() + 1;
    var year = dt.getFullYear();
    const daysInMonth = new Date(year, month, 0).getDate();
    this.loading = true;
    this.roasterAlert = false;
    this.showUpload = true;
    this.httpService.get('/api/getRosterScreenMappingDetails/' + this.customerId + '/' + this.chosenTeam1 + '/' + this.days_in_selected_month + '/' + this.selectedRes + '/' + this.monthNamSelected + '/' + this.itemsPerPage + '/' + this.page)
      .subscribe(data => {
        this.loading = false;
        if (data == 'failure-01') {
          this.message = "No resource were working for the current shift for today.";
          this.roasterAlert = true;
        } else if (data == 'failure-02') {
          this.message = "You are not added shift details for the current month.";
          this.roasterAlert = true;
        } else if (data == 'failure-03') {
          this.message = "No more shift details available for further days of current month.";
          this.roasterAlert = true;
        } else if (Object.keys(data).length != 0) {
          this.app_lst = data;
          this.backup_app_lst = data;
          this.app_lst.map(v => Object.assign(v, { modified: false }));
          this.backup_app_lst.map(v => Object.assign(v, { modified: false }));
          this.modified_records_list = [];
          console.log("data---", data);
        } else {
          this.roasterAlert = true;
          this.message = "No Records Found!"
        }
      },
        err => {
          console.log(err);
          throw "";
        });
    this.httpService.get('/api/getRosterScreenMappingDetails1/' + this.days_in_selected_month)
      .subscribe(data => {
        this.res_shift_lst = data;
        this.backup_app_lst = data;
        console.log(data);
      },
        err => {
          console.log(err);
          throw "";
        });
    this.getResourceApplicationDetails();
    this.getRoasterMappingCount()
    this.httpService.get('/api/getRosterUniqueShifts')
      .subscribe(data => {
        this.shifts = data;
        console.log(data);
      },
        err => {
          console.log(err);
          throw "";
        });
  }
  uploadRoasterDetails() {
    this.loader = true;
    const fileBrowser = this.fileInput2.nativeElement;
    if (fileBrowser.files && fileBrowser.files[0] && this.chosenTeam1 != "") {
      const formData = new FormData();
      formData.append('roasterDetails', fileBrowser.files[0]);
      this.httpService.post('/api/uploadRoasterDetails/' + this.customerId + '/' + this.chosenTeam1, formData, { responseType: 'text' }).subscribe(data => {
        if (data == 'failure') {
          alert('Excel upload is not successful');
          this.loader = false;
          return false;
        }
        if (data['status'] != 'failure') {
          this.loader = false;
          alert("File Uploaded Successfully")
          this.teamChange1();
          this.ngOnInit();
          if (Object.keys(data).length > 1) {
            this.failedRoasterData = data;
            //this.openValidationMessageModal();
          }
        } else {
          console.log('Oops!!, data did not came from backend');
        }
        // this.loader=false;
      }, err => {
        console.log(err);
        throw '';
      });
    } else {
      alert('Please choose the right team and file..!');
      this.loader = false;
    }
  }
  deleteAllRoasters() {
    this.confirmValue = confirm('Are you sure, you want to delete this application?');
    if (this.confirmValue) {
      this.httpService.delete('/api/deleteAllRoasters/' + this.customerId + '/' + this.chosenTeam1, { responseType: 'text' })
        .subscribe(data => {
          this.enableSave = false;
          if (data == 'success') {
            this.ngOnInit();
            this.teamChange1();
          } else {
            console.log(data);
          }
        }, err => {
          console.log(err);
          throw '';
        });
    }
  }
  openValidationMessageModal() {
    const modalRef = this.modalService.open(ValidationMessageComponent, { ariaLabelledBy: 'modal-basic-title', size: "lg" });
    modalRef.componentInstance.failedRoasterUploadDetails = this.failedRoasterData;
    //modalRef.componentInstance.drawGraph();
  }
  // ---Edit rows code---
  editApplication(recordId, index) {
    //this.editRecordId = recordId;    
    this.editRecordId = index;
    //new start
    let prev_resource_shift = this.app_lst[index]['resource_shift']
    let prev_startdate = this.app_lst[index]['start_date']
    let prev_enddate = this.app_lst[index]['end_date']
    this.app_lst[index].prev_startdate = prev_startdate
    this.app_lst[index].prev_enddate = prev_enddate
    this.app_lst[index].prev_resource_shift = prev_resource_shift
    this.app_lst[index].DatasetID = this.dataSetId;
    //new end
    console.log(this.app_lst[index].weekoff);
    if (this.app_lst[index].weekoff == undefined) {
      this.app_lst[index].weekoff = [];
      this.resetModel = new Date(0);
    }
    let uistartdate = moment(this.app_lst[index].start_date);
    this.app_lst[index].start_date = new Date(this.app_lst[index].start_date);
    let uienddate = moment(this.app_lst[index].end_date);
    this.app_lst[index].end_date = new Date(this.app_lst[index].end_date);;
  }
  cancelUpdate() {
    this.editRecordId = -1;
    this.editedDocument = {};
  }
  cancelUpdateNew(i) {
    if (this.app_lst[i].resource_id === 0) {
      this.app_lst.splice(i, 1);
    }
  }
  cloneResource(resource_id, index) {
    const current_resource = Object.assign([], this.app_lst[index]);
    current_resource.temp_resource_id = this.app_lst[index].resource_id;
    current_resource.resource_id = 0;
    current_resource.modified = true;
    this.app_lst.push(current_resource);
  }
  canceldelete(resid, index) {
    let tempStartDate = this.app_lst[index].start_date;
    let tempEndDate = this.app_lst[index].end_date;
    var datePipe = new DatePipe("en-US");
    let startdate = datePipe.transform(tempStartDate, 'yyyy/MM/dd');
    this.app_lst[index].resource_shift = this.app_lst[index].prev_resource_shift;
    this.app_lst[index].start_date = this.app_lst[index].prev_startdate;
    this.app_lst[index].end_date = this.app_lst[index].prev_enddate;
    let enddate = datePipe.transform(tempEndDate, 'yyyy/MM/dd');
    for (let i = 0; i < this.app_lst.length; i++) {
      if (index !== i && this.app_lst[index].resource_id === this.app_lst[i].resource_id) {
        let tempstartdate = this.app_lst[i].start_date;
        let tempenddate = this.app_lst[i].end_date;
        if ((startdate >= tempstartdate && startdate <= tempenddate) ||
          (enddate >= tempstartdate && enddate <= tempenddate)) {
          alert("Date range exists for the resource");
        }
      }
    }
    this.cancelUpdate();
    this.editRecordId = -1;
    this.editedDocument = {};
    this.enableSave = false;
  }
  deleteRow(resid, index) {
    this.confirmValue = confirm('Deleting resource will delete shift details also for the specific roster. Are you sure, you want to delete this roster?');
    this.app_lst[index].DatasetID = this.dataSetId;
    if (this.confirmValue) {
      this.enableSave = true;
      this.deleteRosterList.push(this.app_lst[index]);
      this.app_lst.splice(index, 1);
      this.editRecordId = -1;
      this.editedDocument = {};
    }
  }
  valueChanged(event, fieldName) {
    if (event.target.outerText) {
      this.editedDocument[fieldName] = event.target.outerText;
      console.log("editdocument is: " + this.editedDocument[fieldName]);
    } else {
      alert("Invalid value for field " + fieldName);
    }
  }
  resourceSSelected(name, id, email_id, rowindex) {
    //let index = this.appresourceMappingDetails.findIndex(i => i.resource_id == id);
    this.app_lst[rowindex].resource_name = name;
    this.app_lst[rowindex].temp_resource_id = id;
    this.app_lst[rowindex].email_id = email_id;
    //console.log(this.appresourceMappingDetails);
  }
  shiftSelected(shift, rowindex) {
    this.app_lst[rowindex].resource_shift = shift;
  }
  startDateSelected($event, rowindex) {
    this.app_lst[rowindex].start_date = $event;
  }
  endDateSelected($event, rowindex) {
    this.app_lst[rowindex].end_date = $event;
  }
  updateApplication(recordId, index) {
    let modified_New_resource: any;
    if (this.app_lst[index].resource_name === "" || this.app_lst[index].resource_name == null) {
      alert("Analyst user can't empty");
      return;
    }
    if (this.app_lst[index].resource_shift === "" || this.app_lst[index].resource_shift == null) {
      alert("Resource Shift can't empty");
      return;
    }
    if (this.app_lst[index].start_date === "" || this.app_lst[index].start_date == null) {
      alert("Please select Start date");
      return;
    }
    if (this.app_lst[index].end_date === "" || this.app_lst[index].end_date == null) {
      alert("Please select End date");
      return;
    }
    if (recordId === 0) {
      let tempStartDate = this.app_lst[index].start_date;
      let tempEndDate = this.app_lst[index].end_date;
      var datePipe = new DatePipe("en-US");
      let startdate = datePipe.transform(tempStartDate, 'yyyy/MM/dd');
      let enddate = datePipe.transform(tempEndDate, 'yyyy/MM/dd');
      if ((startdate > enddate)) {
        alert("start date should not be greater than end date")
        return false;
      }
      this.app_lst[index].start_date = startdate;
      this.app_lst[index].end_date = enddate;
      this.app_lst[index].DatasetID = this.dataSetId;
      let weekoffdates = this.app_lst[index].weekoff;
      //Weekoff dates capture - START
      if (weekoffdates != undefined && weekoffdates.length > 0) {
        const dates = [];
        var stdate = datePipe.transform(tempStartDate, 'yyyy/MM/dd');
        var eddate = datePipe.transform(tempEndDate, 'yyyy/MM/dd');
        this.app_lst[index].start_date = stdate;
        this.app_lst[index].end_date = eddate;
        for (let i = 0; i < weekoffdates.length; i++) {
          let datechosen = datePipe.transform(weekoffdates[i], 'yyyy/MM/dd');
          if (datechosen >= stdate && datechosen <= eddate) {
            dates.push(datechosen);
          } else {
            alert("Please select holidays between start date and end date");
            return false;
          }
        }
        this.app_lst[index].weekoff = dates;
      }
      //Weekoff dates capture - START
      //Validation check for duplicate resource with same start and end dates - START
      const resId = this.app_lst[index].temp_resource_id;
      const comparestdate = startdate;
      const compareeddate = enddate;
      const duplicaterec = this.app_lst.filter((val) =>
        val.resource_id === this.app_lst[index].temp_resource_id &&
        val.start_date === comparestdate &&
        val.end_date === compareeddate
        //val.resource_shift ===  this.app_lst[index].resource_shift 
      );
      if (duplicaterec.length > 0) {
        alert("A record with same start and end dates already exists!");
        return;
      }
      //Validation check for duplicate resource with same start and end dates - END
      //Vlidation for date range check - START
      for (let i = 0; i < this.app_lst.length; i++) {
        if (this.app_lst[i].resource_id !== 0 && this.app_lst[i].resource_id === this.app_lst[index].temp_resource_id
          &&
          this.app_lst[i].resource_shift === this.app_lst[index].resource_shift) {
          let tempstartdate = this.app_lst[i].start_date;
          let tempenddate = this.app_lst[i].end_date;
          if ((startdate >= tempstartdate && startdate <= tempenddate) ||
            (enddate >= tempstartdate && enddate <= tempenddate)) {
            alert("Date range exists for the resource");
            return false;
          }
        }
      }
      this.app_lst[index].resource_id = this.app_lst[index].temp_resource_id;
      modified_New_resource = this.app_lst[index];
      this.modified_resource.push(this.app_lst[index]);
      this.app_lst[index].modified = true;
    } else {
      let tempStartDate = this.app_lst[index].start_date;
      let tempEndDate = this.app_lst[index].end_date;
      var datePipe = new DatePipe("en-US");
      let startdate = datePipe.transform(tempStartDate, 'yyyy/MM/dd');
      let enddate = datePipe.transform(tempEndDate, 'yyyy/MM/dd');
      if ((startdate > enddate)) {
        alert("start date should not be greater than end date")
        return false;
      }
      this.app_lst[index].start_date = startdate;
      this.app_lst[index].end_date = enddate;
      const resId = this.app_lst[index].resource_id;
      const comparestdate = startdate;
      const compareeddate = enddate;
      //Validation check for duplicate resource with same start and end dates - START
      const existItem = this.app_lst.filter(x => x.resource_id !== 0 &&
        x.resource_id === resId &&
        x.start_date === startdate && x.end_date === enddate &&
        x.resource_shift === this.app_lst[index].resource_shift);
      if (existItem.length > 1) {
        console.log("A record with same start and end dates already exists!");
        return;
      }
      //Validation check for duplicate resource with same start and end dates - END
      //Vlidation for date range check - START
      for (let i = 0; i < this.app_lst.length; i++) {
        if (index !== i && this.app_lst[index].resource_id === this.app_lst[i].resource_id
          &&
          this.app_lst[i].resource_shift === this.app_lst[index].resource_shift) {
          let tempstartdate = this.app_lst[i].start_date;
          let tempenddate = this.app_lst[i].end_date;
          if ((startdate >= tempstartdate && startdate <= tempenddate) ||
            (enddate >= tempstartdate && enddate <= tempenddate)) {
            alert("Date range exists for the resource");
            return false;
          }
          //
          if ((startdate > enddate)) {
            alert("start date should not be greater than end date")
            return false;
          }
          this.todayDate = new Date();
          let latest_Date1 = this.datePipe.transform(this.todayDate, "yyyy-MM-dd");
          console.log(latest_Date1);
          if (startdate < latest_Date1) {
            alert("Start date cannot be in the past")
            return false;
          }
          //  
        }
      }
      //Vlidation for date range check - END
      let weekoffdates = this.app_lst[index].weekoff;
      //console.log(startdate);
      //console.log(this.app_lst);
      //Weekoff dates capture - START
      if (weekoffdates != undefined && weekoffdates.length > 0) {
        const dates = [];
        var stdate = datePipe.transform(tempStartDate, 'yyyy/MM/dd');
        var eddate = datePipe.transform(tempEndDate, 'yyyy/MM/dd');
        this.app_lst[index].start_date = stdate;
        this.app_lst[index].end_date = eddate;
        for (let i = 0; i < weekoffdates.length; i++) {
          let datechosen = datePipe.transform(weekoffdates[i], 'yyyy/MM/dd');
          if (datechosen >= stdate && datechosen <= eddate) {
            dates.push(datechosen);
          } else {
            alert("Please select holidays between start date and end date");
            return false;
          }
        }
        this.app_lst[index].weekoff = dates;
      }
      //Weekoff dates capture - START
      this.app_lst[index].modified = true;
      modified_New_resource = this.app_lst[index];
      this.modified_resource.push(this.app_lst[index])
      console.log(this.app_lst[index]);
    }
    this.enableSave = true;
    this.cancelUpdate();
    //this.teamChange();
    console.log(this.app_lst);
  }
  // -------------------
  saveRosterDetails() {
    const nonsavedRows = this.app_lst.filter((val) =>
      val.resource_id === 0
    );
    if (nonsavedRows !== undefined && nonsavedRows.length > 0) {
      alert("There are unsaved rows, please save them");
      return false;
    }
    this.loading = true;
    this.modified_records_list = this.app_lst.filter((val) =>
      val.modified === true
    );
    this.getMonthName_days_of_month(new Date().getMonth() + 1);
    var dt = new Date();
    var month = dt.getMonth() + 1;
    var year = dt.getFullYear();
    const daysInMonth = new Date(year, month, 0).getDate();
    //
    var resource_list = []
    console.log("Before resource_list", resource_list)
    for (let i in this.modified_records_list) {
      if (this.modified_records_list[i]['modified'] == true)
        resource_list.push(this.modified_records_list[i]['resource_name'])
    }
    console.log("Before 11 resource_list", resource_list)
    let resourceSet = new Set(resource_list)
    console.log("resourceSet", resourceSet)
    let resource_list_final = []
    resource_list_final = Array.from(resourceSet.values())
    console.log("resource_list_final", resource_list_final)
    const delete_list = []
    for (let i in this.deleteRosterList) {
      if (this.deleteRosterList[i]['modified'] == true)
        delete_list.push(this.deleteRosterList[i]['resource_name'])
      console.log("delllll", delete_list)
    }
    let deleteSet = new Set(delete_list)
    console.log("deleteSet", deleteSet)
    let delete_list_final = []
    delete_list_final = Array.from(deleteSet.values())
    resource_list = [];
    for (let i in this.modified_resource) {
      //if(this.modified_resource[i]['modified'] == true)
      resource_list.push(this.modified_resource[i]['resource_name'])
    }
    console.log(resource_list)
    let resource_list_final_new = '';
    resource_list_final_new = resource_list.toString()
    let delete_list_new = [];
    for (let i in this.deleteRosterList) {
      //if(this.modified_resource[i]['modified'] == true)
      delete_list_new.push(this.deleteRosterList[i]['resource_name'])
    }
    console.log(delete_list)
    let delete_list_final_new = '';
    delete_list_final_new = delete_list_new.toString()
    let data = { "modifiedRosterDetails": this.modified_records_list, "deleteRosterList": this.deleteRosterList };
    console.log(this.modified_records_list);
    this.httpService
      .post(
        "/api/updateRosterMappingDetails/" + daysInMonth,
        //this.app_lst,
        //this.modified_records_list,
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
          this.getlatestDataPostSave();
          if (resource_list.length != 0 && delete_list.length != 0) {
            alert("Roster add updated successfully for " + resource_list_final_new + "!" + "Roster delete updated successfully for " + delete_list_final_new + "!")
          }
          if (resource_list.length > 0 && delete_list.length == 0) {
            alert("Roster add updated successfully for " + resource_list_final_new + "!");
          }
          else {
            alert("Roster deleted successfully for " + delete_list_final_new + "!");
          }
          this.ngOnInit();
          this.modified_resource = [];
          this.deleteRosterList = [];
        }
        else {
          alert("Failed to update roster for " + resource_list_final_new + delete_list_final_new + "! Please check resource details and mapping details!");
          this.modified_resource = [];
          this.deleteRosterList = [];
          this.ngOnInit();
        }
      },
        err => {
          console.log(err);
          this.loading = false;
          throw '';
        });
    // this.pageChanged();
  }
  validateDates(sDate: string, eDate: string) {
    this.todayDate = new Date();
    let firstDate = this.datePipe.transform(sDate, "dd-MM-yyyy")
    let secondDate = this.datePipe.transform(eDate, "dd-MM-yyyy")
    let latest_Date = this.datePipe.transform(this.todayDate, "dd-MM-yyyy");
    this.isValidDate = true;
    if ((firstDate == null || secondDate == null)) {
      this.error = { isError: true, errorMessage: 'Start date and end date are required.' };
      this.isValidDate = false;
    }
    if ((firstDate != null && secondDate != null) && ((secondDate) < (firstDate)) || (firstDate) < (latest_Date)) {
      this.error = { isError: true, errorMessage: 'End date should be grater then start date.' };
      this.isValidDate = false;
    }
    return this.isValidDate;
  }
  deleteApplication(recordId: string) {
    this.confirmValue = confirm(
      "Are you sure!, you want to delete this application?"
    );
    if (this.confirmValue) {
      this.httpService
        .delete(
          "/api/deleteApplication/" +
          this.customerId +
          "/" +
          this.chosenTeam +
          "/" +
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
  changeView(val) {
    const tableView = document.getElementById("table") as HTMLElement;
    const gridView = document.getElementById("grid") as HTMLElement;
    if (val === "table") {
      this.tableView = true;
      this.gridView = false;
      tableView.style.color = "#9c27b0";
      gridView.style.color = "darkgrey";
    }
    if (val === "grid") {
      this.gridView = true;
      this.tableView = false;
      tableView.style.color = "darkgrey";
      gridView.style.color = "#9c27b0";
    }
  }
  public getMonthDays(daysCount: number): Array<number> {
    const resultArray = [];
    for (let i = 1; i <= daysCount; ++i) {
      if (i < 10) resultArray.push("0" + i);
      else resultArray.push(i);
    }
    return resultArray;
  }
  public findResource($event) {
    if ($event !== "") {
      console.log("findresource()")
      this.resources = this.backupResources.slice();
      console.log("searchhhh", this.resources)
      this.resources = this.resources.filter((val) =>
        val.resource_name.toLowerCase().includes($event.toLowerCase())
      );
    } else {
      this.resources = this.backupResources.slice();
    }
  }
  public monthSelected(month: any) {
    this.monthNamSelected = month;
    this.searchResource(this.resource);
  }
  public searchResource($event) {
    let value = this.months.filter((val) => val.month == this.monthNamSelected);
    this.selected_Month = value[0].month;
    this.selected_Month_id = value[0]._id;
    this.days_in_selected_month = value[0].days;
    console.log("iNSIDE SEARCH rESOUCE")
    console.log("$event", $event);
    this.selectedRes = "All";
    if ($event.resource_name !== undefined) {
      this.selectedRes = $event.resource_name;
    }
    this.getRoasterMappingCount();
    this.pageChanged();
  }
  checkResourceformonth(monthselected, stdate, edate) {
    console.log("monthandstdate", monthselected, stdate);
    let MonthNum = { "January": 0, "February": 1, "March": 2, "April": 3, "May": 4, "June": 5, "July": 6, "August": 7, "September": 8, "October": 9, "November": 10, "December": 11 }
    let count = 0;
    let resStarteddate = new Date(stdate);
    let resEndedDate = new Date(edate)
    let resMonthStart = resStarteddate.getMonth();
    let resMonthEnd = resEndedDate.getMonth();
    let monthSelNum = MonthNum[monthselected]
    // console.log(resMonthEnd,monthSelNum)
    // if (resMonthStart == monthselected || resMonthEnd == monthselected) {
    if (resMonthStart == monthSelNum || resMonthEnd == monthSelNum || (resMonthStart <= monthSelNum && resMonthEnd >= monthSelNum)) {
      return true
    } else {
      return false;
    }
  }
  public searchResource_new($event) {
    console.log($event);
    this.resource = $event;
    console.log(this.resource);
    if (this.resource !== "All" && this.months.length == 0) {
      let new_list = this.backup_app_lst.slice();
      this.app_lst = new_list.filter((val) => {
        if (
          val.resource_name === this.resource &&
          this.checkApplication(this.months, val.resorce_name)
        ) {
          return val;
        }
      });
      console.log(this.app_lst);
    } else if (this.resource !== "All" && this.months.length === 0) {
      let new_list = this.backup_app_lst.slice();
      this.app_lst = new_list.filter(
        (val) => val.resource_name === this.resource
      );
      console.log(this.app_lst);
    } else {
      this.app_lst = this.backup_app_lst;
    }
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
  clearSearch(value) {
    if (value === "User") {
      this.searchGroup = "";
      this.resources = this.backupResources.slice();
    }
  }
  getMonthName_days_of_month(month_no) {
    let value = this.months.filter((val) => val._id === month_no);
    this.selected_Month = value[0].month;
    this.selected_Month_id = value[0]._id;
    this.days_in_selected_month = value[0].days;
    this.monthNamSelected = value[0].month;
  }
  Re_generateHeatMap($event) { }
  WeightedAverage_typechanged($event) { }
  public datePickerRow(rowIndex: any) {
    this.rowSelectedinTable = rowIndex;
  }
  public dateClass = (date: Date) => {
    if (this._findDate(date) !== -1) {
      return ['selected'];
    }
    return [];
  }
  public dateChanged(event: MatDatepickerInputEvent<Date>, rowIndex): void {
    if (event.value) {
      const date = event.value;
      const index = this._findDate(date);
      if (index === -1) {
        this.app_lst[rowIndex].weekoff.push(date);
      }
      else {
        this.app_lst[rowIndex].weekoff.splice(index, 1);
      }
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
  public remove(date: Date, rowIndex): void {
    const index = this._findDateforremoval(date, rowIndex);
    this.app_lst[rowIndex].weekoff.splice(index, 1);
  }
  private _findDateforremoval(date: Date, rowIndex): number {
    return this.app_lst[rowIndex].weekoff.indexOf(date);
  }
  private _findDate(date: Date): number {
    const rowIndex = this.rowSelectedinTable;
    return this.app_lst[rowIndex].weekoff.map((m) => +moment(m)).indexOf(+date);
  }
  getKeyByValue(object, value) {
    return Object.keys(object).find(key => object[key] === value);
  }
}
