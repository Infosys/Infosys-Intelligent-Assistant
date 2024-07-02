/* Copyright 2022 Infosys Ltd.Use of this source code is governed by MIT license that can be found in the LICENSE file or athttps://opensource.org/licenses/MIT.*/
import { Component, OnInit } from '@angular/core';
import { FormBuilder, FormControl, FormArray, FormGroup } from '@angular/forms';
import { HttpClient } from '@angular/common/http';
import { ResponseType } from '@angular/http';
import { text } from '@angular/core/src/render3';
@Component({
  selector: 'app-team-details',
  templateUrl: './team-details.component.html',
  styleUrls: ['./team-details.component.css']
})
export class TeamDetailsComponent implements OnInit {
  editField: string;
  removeAllTeams: boolean = false;;
  saveStatus: boolean;
  removeStatus: boolean;
  customerId: number = 1;
  teamsToBeDeleted: Array<number> = [];
  teamsToBeAdded: Array<number> = [];
  teamList: any = [];
  totalTeams: number;
  oneChecked = false;
  successMessage = false;
  message = '';
  loading = false;
  constructor(private httpClient: HttpClient) { }
  ngOnInit() {
    this.getTeam();
  }
  getTeam() {
    this.httpClient.get('/api/getTeamNameWithId/' + this.customerId).subscribe(data => {
      this.teamList = data;
      this.totalTeams = this.teamList.length;
      this.teamList.forEach(team => {
        team['Selected'] = false;
      });
    });
  }
  remove(id: any) {
    // this.awaitingPersonList.push(this.personList[id]);
  }
  add() {
    let len = this.teamList.length;
    if (this.teamList.length > 0 && this.teamList[len - 1]['TeamName'] != '') {
      this.teamList.push({ 'TeamName': '', 'Selected': false });
      this.totalTeams = this.totalTeams + 1;
    } else if (this.teamList.length == 0) {
      this.totalTeams = 1;
      this.teamList.push({ 'TeamName': '', 'Selected': false });
    }
  }
  changeValue(id: number, event: any, team) {
    this.editField = event.target.textContent;
    var nameFormat = /^[a-zA-Z0-9 _.-]*$/;
    if (this.editField.trim() == "") {
      alert("Team name can't be empty");
      return;
    }
    if (!nameFormat.test(String(this.editField).toLowerCase().trim())) {
      alert("Team name is invalid");
      return;
    }
    if (this.editField == '') {
      this.teamList = this.teamList;
    } else {
      this.teamList.splice(id, 1, { 'TeamName': this.editField, 'TeamID': team.TeamID, 'Selected': false });
    }
  }
  selectAll() {
    let index = 0;
    if (this.removeAllTeams) {
      this.teamList.forEach(team => {
        team['Selected'] = true;
        this.teamsToBeDeleted.push(index);
        this.teamsToBeAdded.push(index);
        index++;
      });
    } else {
      this.teamList.forEach(team => {
        team['Selected'] = false;
      });
      this.teamsToBeDeleted = [];
      this.teamsToBeAdded = [];
    }
  }
  checkIfAllSelected(id: number) {
    // let index=0;
    if (this.teamList[id]['Selected'] == true) {
      this.oneChecked = true;
      this.teamsToBeDeleted.push(id);
      this.teamsToBeAdded.push(id);
    } else {
      this.teamsToBeDeleted.splice(this.teamsToBeDeleted.indexOf(id), 1);
      this.teamsToBeAdded.splice(this.teamsToBeAdded.indexOf(id), 1);
      this.oneChecked = false;
    }
    if (this.totalTeams == this.teamsToBeDeleted.length || this.totalTeams == this.teamsToBeAdded.length) {
      this.removeAllTeams = true;
    } else {
      this.removeAllTeams = false;
    }
  }
  removeTeams() {
    this.successMessage = false;
    var deleteTeamsId: any = [];
    if (this.teamsToBeDeleted.length > 0) {
      this.teamsToBeDeleted.forEach(index => {
        if (this.teamList[index]['TeamID']) {
          deleteTeamsId.push(this.teamList[index]['TeamID']);
        }
      });
      this.loading = true;
      if (deleteTeamsId.length > 0) {
        this.httpClient.delete('/api/removeTeam/' + this.customerId + '/' + deleteTeamsId, { responseType: 'text' })
          .subscribe(data => {
            console.log('success');
            this.loading = false;
            this.successMessage = true;
            this.message = "Team Details Removed Successfully"
            this.teamsToBeDeleted = this.teamsToBeDeleted.sort();
            this.teamsToBeDeleted = this.teamsToBeDeleted.reverse();
            this.teamsToBeDeleted.forEach(index => {
              this.teamList.splice(index, 1);
            });
            this.teamsToBeDeleted = [];
            this.getTeam();
          });
      } else {
        this.loading = false;
        this.teamList.pop();
        this.teamsToBeDeleted = [];
      }
    }
    this.removeAllTeams = false;
  }
  addTeams() {
    this.successMessage = false;
    let len = this.teamList.length;
    if (this.teamsToBeAdded.length == 0) {
      this.teamList.forEach(index => {
        index.Selected = true;
      })
    }
    if (this.teamList.length > 0 && this.teamList[len - 1]['TeamName'] == '') {
      this.teamList[len - 1]['Selected'] = false;
      alert("Team Name can't empty");
      return;
      this.teamList.pop();
    }
    this.loading = true;
    this.httpClient.post('/api/addTeam/' + this.customerId, this.teamList, { responseType: "text" })
      .subscribe(data => {
        console.log('success');
        this.loading = false;
        this.successMessage = true;
        this.message = "Team Details Added Successfully";
        this.getTeam();
        this.removeAllTeams = false;
        this.teamsToBeAdded = [];
        this.teamsToBeDeleted = [];
      })
  }
}
