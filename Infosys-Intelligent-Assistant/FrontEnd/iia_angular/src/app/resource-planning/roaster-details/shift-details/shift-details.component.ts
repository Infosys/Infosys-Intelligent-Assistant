/* Copyright 2022 Infosys Ltd.Use of this source code is governed by MIT license that can be found in the LICENSE file or athttps://opensource.org/licenses/MIT.*/
import { Component, OnInit, ViewChild, ElementRef } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { HttpErrorResponse } from '@angular/common/http';
import { ActivatedRoute, ParamMap } from '@angular/router';
import { Router } from '@angular/router';
@Component({
  selector: 'app-shift-details',
  templateUrl: './shift-details.component.html',
  styleUrls: ['./shift-details.component.css']
})
export class ShiftDetailsComponent implements OnInit {
  shift_lst: any = [];
  resourceName: string = "";
  startDate: string;
  endDate: string;
  customerId: number = 1;
  teamName: string;
  emialId: string;
  constructor(private httpService: HttpClient, private route: ActivatedRoute, private router: Router) {
  }
  ngOnInit() {
    this.resourceName = this.route.snapshot.paramMap.get('resourceName');
    this.teamName = this.route.snapshot.paramMap.get('chosenTeam');
    this.customerId = Number(this.route.snapshot.paramMap.get('customerId'));
    this.emialId = this.route.snapshot.paramMap.get('emailId')
    this.showShiftDetails()
  }
  showShiftDetails() {
    console.log('customerId' + this.customerId + 'teamName' + this.teamName + 'resourceName' + this.resourceName)
    this.httpService.get("/api/getShiftDetails/" + this.customerId + "/" + this.teamName + "/" + this.emialId)
      .subscribe(data => {
        if (data != 'failure') {
          this.shift_lst = data;
        } else {
          console.log('No data found from backend')
        }
      }, err => {
        console.log(err);
        throw '';
      });
  }
  updateRoasterDetails() {
    this.httpService.put("/api/updateRoaster/" + this.customerId + "/" + this.teamName + "/" + this.emialId + "/" + this.startDate + "/" + this.endDate, null, { responseType: 'text' })
      .subscribe(data => {
        if (data == 'success') {
          this.showShiftDetails()
        } else {
          console.log(data);
        }
      }, err => {
        console.log(err);
        throw '';
      });
  }
  goBack() {
    this.router.navigate(['/resourceplanning']);
  }
}
