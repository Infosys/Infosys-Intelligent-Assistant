/* Copyright 2022 Infosys Ltd.Use of this source code is governed by MIT license that can be found in the LICENSE file or athttps://opensource.org/licenses/MIT.*/
import { Component, OnInit, ViewChild, ElementRef } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Router } from '@angular/router';
import { HttpErrorResponse } from '@angular/common/http';
import { MatDialog } from '@angular/material';
@Component({
  selector: 'app-ticket-weightage-details',
  templateUrl: './ticket-weightage.component.html',
  styleUrls: ['./ticket-weightage.component.css']
})
export class TicketWeightageComponent implements OnInit {
  @ViewChild('ticketWeightageDetails') fileInput: ElementRef;
  hasTicketWeightageDetails: boolean = false;
  ticketWeightageList: any = [];
  teams: any = [];
  customerId: number = 1;
  chosenTeam: string;
  showUpload: boolean;
  constructor(private httpService: HttpClient, private router: Router) {
    this.httpService.get('/api/getDatasetTeamNames/' + this.customerId).subscribe(data => {
      if (data['Teams'].length > 0) {
        console.log('data from getdatasetteamnames methode: ' + data['Teams'] + data['DatasetIDs'])
        this.teams = data['Teams'];
        this.httpService.get('/api/getTicketWeightageTeamNames', { responseType: 'text' }).subscribe(team => {
          if (team != 'no team') {
            this.chosenTeam = team;
            this.teamChange();
          }
        });
      } else {
        alert('No Dataset found!. Create Dataset to proceed with uploading of assignment details');
      }
    }, err => {
      console.log(err);
      throw '';
    });
  }
  ngOnInit() { }
  teamChange() {
    this.showUpload = true;
    this.httpService.get('/api/getTicketWeightage/' + this.customerId + '/' + this.chosenTeam)
      .subscribe(data => {
        if (Object.keys(data).length != 0) {
          this.ticketWeightageList = data;
          this.hasTicketWeightageDetails = true;
        } else {
          this.hasTicketWeightageDetails = false;
          this.ticketWeightageList = [];
        }
      }, err => {
        console.log(err);
        throw '';
      });
  }
  uploadTicketWeightageDetails() {
    const fileBrowser = this.fileInput.nativeElement;
    if (fileBrowser.files && fileBrowser.files[0]) {
      const formData = new FormData();
      formData.append('ticketWeightageDetails', fileBrowser.files[0]);
      this.httpService.post('/api/uploadTicketWeightage/' + this.customerId + '/' + this.chosenTeam, formData, { responseType: 'text' })
        .subscribe(data => {
          if (data == 'success') {
            this.hasTicketWeightageDetails = true;
            this.teamChange();
          } else {
            this.hasTicketWeightageDetails = false;
          }
        });
    }
  }
  deleteAllTicketWeightage() {
    let confirmValue = confirm('Are you sure!, you want to delete all applications?');
    if (confirmValue) {
      this.httpService.delete('/api/deleteAllTicketWeightage/' + this.customerId + '/' + this.chosenTeam, { responseType: 'text' })
        .subscribe(data => {
          if (data == 'success') {
            this.hasTicketWeightageDetails = false;
          } else {
            console.log(data);
          }
        });
    }
  }
}