/* Copyright 2022 Infosys Ltd.Use of this source code is governed by MIT license that can be found in the LICENSE file or athttps://opensource.org/licenses/MIT.*/
import { Component, ViewChild, ElementRef, QueryList, ViewChildren } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { HttpErrorResponse } from '@angular/common/http';
import { Router } from '@angular/router';
import { NgbModal, NgbActiveModal, ModalDismissReasons } from '@ng-bootstrap/ng-bootstrap';
import { ValidationMessageComponent } from '../validation-message/validation-message.component'
import { MatDatepicker, MatDatepickerInputEvent } from '@angular/material/datepicker';
@Component({
  selector: 'app-roaster-details',
  templateUrl: './roaster-details.component.html',
  styleUrls: ['./roaster-details.component.css']
})
export class RoasterDetailsComponent {
  @ViewChild('roasterDetails') fileInput: ElementRef;
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
  showShiftDetails: boolean = false;
  hasRoasterDetails: boolean = false;
  showUpload: boolean = false;
  roasterAlert: boolean;
  loader: boolean;
  roasterResourceDetails: any = [];
  teams: any = [];
  resourceName: string = "";
  customerId: number = 1;
  chosenTeam: string = "";
  confirmValue: boolean;
  failedRoasterData: any = [];
  emailId: string;
  message: string;
  sampleArray: any =
    [
      { "id": 0, "model": [new Date('7/15/1966'), new Date('7/15/1967')] },
      { "id": 1, "model": [new Date('7/15/1998'), new Date('7/15/1999')] }
    ];
  rowSelectedinTable: any = 0;
  constructor(private httpService: HttpClient, private router: Router, private modalService: NgbModal) {
    this.httpService.get('/api/getDatasetTeamNames/' + this.customerId).subscribe(data => {
      if (data['Teams'].length > 0) {
        console.log('data from getdatasetteamnames methode: ' + data['Teams'] + data['DatasetIDs'])
        this.teams = data['Teams'];
        this.httpService.get('/api/getRoasterTeamNames', { responseType: 'text' }).subscribe(team => {
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
    this.showUpload = true;
    this.httpService.get('/api/getRoasterDetails/' + this.customerId + '/' + this.chosenTeam).subscribe(data => {
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
        this.roasterResourceDetails = data;
        this.hasRoasterDetails = true;
        this.roasterAlert = false;
      } else {
        this.hasRoasterDetails = false;
        this.roasterResourceDetails = [];
        this.roasterAlert = false;
      }
    }, err => {
      console.log(err);
      throw '';
    });
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
        this.sampleArray[rowIndex].model.push(date);
      } else {
        this.sampleArray[rowIndex].model.splice(index, 1);
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
  public remove(date: Date): void {
    const index = this._findDate(date);
    this.model.splice(index, 1)
  }
  private _findDate(date: Date): number {
    const rowIndex = this.rowSelectedinTable;
    return this.sampleArray[rowIndex].model.map((m) => +m).indexOf(+date);
  }
  uploadRoasterDetails() {
    this.loader = true;
    const fileBrowser = this.fileInput.nativeElement;
    if (fileBrowser.files && fileBrowser.files[0] && this.chosenTeam != "") {
      const formData = new FormData();
      formData.append('roasterDetails', fileBrowser.files[0]);
      this.httpService.post('/api/uploadRoasterDetails/' + this.customerId + '/' + this.chosenTeam, formData).subscribe(data => {
        if (data['status'] != 'failure') {
          this.teamChange();
          if (Object.keys(data).length > 1) {
            this.failedRoasterData = data;
            this.openValidationMessageModal();
          }
        } else {
          console.log('Oops!!, data did not came from backend');
        }
        this.loader = false;
      }, err => {
        console.log(err);
        throw '';
      });
    } else {
      alert('Please choose the right team and file..!');
      this.loader = false;
    }
  }
  onSelect(emailId: string, resourceName: string) {
    this.resourceName = resourceName;
    this.emailId = emailId;
    this.router.navigate(['/shiftdetails', this.customerId, this.chosenTeam, this.emailId, this.resourceName]);
  }
  deleteAllRoasters() {
    this.confirmValue = confirm('Are you sure, you want to delete this application?');
    if (this.confirmValue) {
      this.httpService.delete('/api/deleteAllRoasters/' + this.customerId + '/' + this.chosenTeam, { responseType: 'text' })
        .subscribe(data => {
          if (data == 'success') {
            this.teamChange();
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
  }
}
