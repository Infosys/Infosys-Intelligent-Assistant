/* Copyright 2022 Infosys Ltd.Use of this source code is governed by MIT license that can be found in the LICENSE file or athttps://opensource.org/licenses/MIT.*/
import { Component, OnInit, ViewChild, ElementRef, Output, EventEmitter } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Http, RequestOptions, Headers } from '@angular/http';
import { Router } from '@angular/router';
import { Subscription } from 'rxjs/Subscription';
import { NgbModal, NgbActiveModal } from '@ng-bootstrap/ng-bootstrap';
import { RelatedTicketsComponent } from '../ticket/related-tickets/related-tickets.component';
@Component({
  selector: 'predict',
  templateUrl: './predict.component.html',
  styleUrls: ['./predict.component.css']
})
export class PredictComponent implements OnInit {
  @ViewChild('filename') fileInput: ElementRef;
  uploadSuccess: boolean = false;
  postResult: any;
  algorithmChosen: boolean = false;
  customerId: number = 1;
  predictedFields: any = [];
  algorithms: any = [];
  checked: boolean = false;
  loading: boolean = false;
  serviceNow: boolean = true;
  serviceNowTickets: any = [];
  csvTickets: boolean = false;
  loadingITSM: boolean = false;
  predictStatus: boolean = false;
  teams: any = {};
  allDatasets: any = [];
  datasets: any = [];
  details: any = [];
  selectedDataset: number;
  firstPredDataSetId: number;
  userLoginState: boolean = false;
  adminLoginState: boolean = false;
  datasetID: number;
  chosenTeam: any;
  teamId: number;
  otherFields: any[];
  filterFields: any[];
  constructor(private httpClient: HttpClient, private router: Router, private modalService: NgbModal) {
    this.getCSVTickets();
  }
  ngOnInit() {
    let userType = localStorage.getItem('Access')
    if (userType == 'User') { this.userLoginState = true }
    if (userType == 'Admin') { this.adminLoginState = true }
  }
  uploadTickets() {
    console.log('in uploadTickets');
    console.log(this.fileInput.nativeElement.value);
    const fileBrowser = this.fileInput.nativeElement;
    if (fileBrowser.files && fileBrowser.files[0]) {
      this.loading = true;
      const formData = new FormData();
      formData.append('files', fileBrowser.files[0]);
      this.httpClient.post('/api/insert/' + this.customerId, formData, { responseType: 'text' })
        .subscribe(msg => {
          msg = msg.replace('"', "").replace('"', "")
          console.log('msg getting...' + msg)
          if (msg == "failure") {
            alert("Error: Supports only csv file format. please upload csv file.")
            this.loading = false;
          } else {
            this.loading = false;
            this.uploadSuccess = true;
            this.postResult = "File uploaded successfully! Click \"Predict\" to continue.";
            console.log(this.postResult);
            if (msg == "success") {
              this.predictTickets();
            } else {
              this.uploadSuccess = false;
              alert("Do not match with any of the datasets.")
            }
          }
        },
          err => {
            console.log(err);
            throw "";
          });
    } else {
      this.loading = false;
    }
  }
  predictTickets() {
    this.predictStatus = true;
    console.log('in predictTickets');
    this.httpClient.get('/api/predict/' + this.customerId).subscribe(data => {
      this.selectedDataset = data['DatasetID'];
      this.predictStatus = false;
      this.router.navigate(['/tickets', this.selectedDataset]);
    });
  }
  predictServiceNowTickets() {
    this.predictStatus = true;
    this.httpClient.get('/api/predict/' + this.customerId).subscribe(data => {
      this.selectedDataset = data['DatasetID'];
      this.predictStatus = false;
      this.router.navigate(['/tickets', this.selectedDataset]);
    });
  }
  getServiceNowTickets() {
    this.loadingITSM = true;
    this.serviceNow = true;
    this.csvTickets = false;
    //this.httpClient.get('/api/serviceNow/' + this.customerId).subscribe(data => {
    this.httpClient.get('/api/invoke_ITSM_adapter/' + this.customerId).subscribe(data => {
      this.loadingITSM = false;
      console.log('in getServiceNowTickets');
      if (data[0] != undefined) {
        this.serviceNowTickets = data;
        this.selectedDataset = data[0]['DatasetID'];
        this.predictServiceNowTickets();
      } else {
        alert('No Tickets received from service now! Please confirm that you have given correct login credentials.');
      }
    });
  }
  getCSVTickets() {
    this.loadingITSM = false;
    this.csvTickets = true;
    this.serviceNow = false;
  }
  ShowPreviousPredictedDetails() {
    this.loadingITSM = true;
    this.httpClient.get('/api/getfirstPredDataSetID').subscribe(data => {
      if (data != null && data != "Failure") {
        this.loadingITSM = false;
        this.firstPredDataSetId = data["DatasetID"] as number;
        // PPT : Previously Predicted Tickets
        let custIdPPD = this.firstPredDataSetId + ',PPT';
        if (this.firstPredDataSetId > 0) {
          // this.router.navigate(['/tickets', this.firstPredDataSetId]);
          this.router.navigate(['/tickets', custIdPPD]);
        }
        else {
          this.loadingITSM = false;
          alert('There are no previously predicted data');
        }
      }
      else {
        this.loadingITSM = false;
        alert('There are no previously predicted data');
      }
    });
  }
  private showRelatedTickets(incidentNumber: string, description: string) {
    const modalRef = this.modalService.open(RelatedTicketsComponent, { size: 'lg', backdrop: false });
    let dataPassToChild: any = {};
    dataPassToChild['DatasetID'] = this.selectedDataset;
    dataPassToChild['IncidentNumber'] = incidentNumber;
    dataPassToChild['Description'] = description;
    dataPassToChild['PredictRadio'] = "ITSM";
    (<RelatedTicketsComponent>modalRef.componentInstance).dataToTakeAsInput = dataPassToChild;
    modalRef.result.then((result) => {
      console.log(result);
    }).catch((result) => {
      console.log(result);
    });
  }
  ticketsAssignedToMe() {
    this.loadingITSM = true;
    this.httpClient.get('/api/getfirstPredDataSetID').subscribe(data => {
      console.log(data);
      if (data != null && data != "Failure") {
        this.loadingITSM = false;
        this.firstPredDataSetId = data["DatasetID"] as number;
        // ATM : Assigned To Me
        let custIdATM = this.firstPredDataSetId + ',ATM';
        if (this.firstPredDataSetId > 0) {
          this.router.navigate(['/tickets', custIdATM]);
        }
        else {
          this.loadingITSM = false;
          alert('There are no previously predicted data');
        }
      }
      else {
        this.loadingITSM = false;
        alert('There are no previously predicted data');
      }
    });
  }
}
