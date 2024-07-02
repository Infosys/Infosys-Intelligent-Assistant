/* Copyright 2022 Infosys Ltd.Use of this source code is governed by MIT license that can be found in the LICENSE file or athttps://opensource.org/licenses/MIT.*/
import { Component, OnInit } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Router } from '@angular/router';
declare const $: any;
declare interface RouteInfo {
  path: string;
  title: string;
  class: string;
  icon_class: string;
}
export const ROUTES: RouteInfo[] = [
  { path: '/workbench', title: 'Workbench', class: '', icon_class: 'fa fa-bar-chart' },
  { path: '/predict', title: 'Predict', class: '', icon_class: 'fa fa-product-hunt' }
];
@Component({
  selector: 'app-sidebar',
  templateUrl: './sidebar.component.html',
  styleUrls: ['./sidebar.component.css']
})
export class SidebarComponent implements OnInit {
  switchStatus: boolean;
  predictionStatus: boolean;
  menuItems: any[];
  adminLoginState: boolean;
  firstPredDataSetId: number;
  customerId: number = 1;
  chosenTeam: string = "";
  teams: any = [];
  constructor(private httpClient: HttpClient, private httpService: HttpClient, private router: Router) { }
  ngOnInit() {
    this.httpService.get('/api/getDatasetTeamNames/' + this.customerId).subscribe(data => {
      if (data['Teams'].length > 0) {
        this.teams = data['Teams'];
        this.httpService.get('/api/getApplicationTeamNames', { responseType: 'text' }).subscribe(team => {
          if (team != 'no team') {
            this.chosenTeam = team;
            this.getStatus();
          }
        });
      } else {
        console.log('No Dataset found!. Create Dataset to proceed with uploading of assignment details');
      }
    }, err => {
      console.log(err);
      throw '';
    });
    let userType = localStorage.getItem('Access')
    if (userType == 'Admin') { this.adminLoginState = true }
    this.menuItems = ROUTES.filter(menuItem => menuItem);
    //this.getStatus();
  }
  getStatus() {
    this.httpClient.get("/api/getSwitchStatus" + '/' + this.customerId + '/' + this.chosenTeam).subscribe(data => {
      let status = data['assignment_enabled']
      if (status == 'true') { this.switchStatus = true; } else { this.switchStatus = false; }
      let predictionStatus = data['prediction_enabled']
      if (predictionStatus == 'true') {
        this.predictionStatus = true;
      } else {
        this.predictionStatus = false;
      }
    });
  }
  isMobileMenu() {
    if ($(window).width() > 991) {
      return false;
    }
    return true;
  };
}
