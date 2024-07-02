/* Copyright 2022 Infosys Ltd.Use of this source code is governed by MIT license that can be found in the LICENSE file or athttps://opensource.org/licenses/MIT.*/
import { Component, OnInit } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Router } from '@angular/router';
import { ResponseType } from '@angular/http';
@Component({
  selector: 'app-notifications',
  templateUrl: './notifications.component.html',
  styleUrls: ['./notifications.component.css']
})
export class NotificationsComponent implements OnInit {
  hasTrainingStateDetails: boolean;
  customerId: number = 1;
  datasetId: number;
  trainingStateList: any = [];
  displayJobs: boolean = false;
  jobs: any = [];
  jobStatus: string;
  jobstopped: boolean = false;
  clickcount: number;
  jobstoppedflag: boolean;
  constructor(private httpService: HttpClient, private router: Router) {
  }
  ngOnInit() {
    this.getTrainingStateData();
  }
  getJobs() {
    this.clickcount = 0;
    this.httpService.get('/api/GetJobs/' + this.customerId).subscribe(data => {
      if ((data[0] == "failure") && (this.jobstopped == false)) {
        this.jobstoppedflag = false;
        this.clickcount++;
        if (this.clickcount == 1) {
          console.log("there are no jobs to display so display in HTML ")
        }
        this.displayJobs = false;
      }
      else {
        this.displayJobs = true;
        this.jobs = data;
      }
      if ((data[0] == "failure") && (this.jobstopped == true)) {
        this.displayJobs = false;
        this.jobstoppedflag = true;
        this.jobstopped = false;
      }
    });
  }
  stopJob(job_id) {
    this.datasetId = Number(job_id.charAt(1));
    this.httpService.get('/api/StopJob/' + this.customerId + '/' + this.datasetId + '/' + job_id, { responseType: 'text' }).subscribe(resp => {
      if (resp == 'failure') {
        console.log("Error in stopping Job");
      }
      else {
        this.jobstopped = true;
        this.getJobs();//if we call this function now ,it checks for active jobs but we dont have now 
      }
    });
  }
  getTrainingStateData() {
    this.httpService.get('/api/getTrainingState/' + this.customerId, { responseType: 'json' }).subscribe(data => {
      if (data != 'empty') {
        this.hasTrainingStateDetails = true;
        this.trainingStateList = data;
      } else {
        this.trainingStateList = [];
      }
    });
  }
  toTrainingPage(datasetId: number) {
    this.router.navigate(['/algorithminformation', datasetId]);
  }
}