/* Copyright 2022 Infosys Ltd.Use of this source code is governed by MIT license that can be found in the LICENSE file or athttps://opensource.org/licenses/MIT.*/
import { Component, OnInit } from '@angular/core';
import { HttpClient } from '@angular/common/http';
@Component({
  selector: 'app-itsm-details',
  templateUrl: './itsm-details.component.html',
  styleUrls: ['./itsm-details.component.css']
})
export class ITSMDetialsComponent implements OnInit {
  userId: string = '';
  password: string = '';
  toolName: string = '';
  showMessage: boolean = false;
  toolNameOthers: string = '';
  ITSMToolNames: any;
  userFormat: any;
  passwordFormat: any;
  toolNameFormat: any;
  hide: boolean = false;
  constructor(private httpClient: HttpClient) {
    this.httpClient.get('/api/getITSMTools').subscribe((data) => {
      this.ITSMToolNames = data['ITSMToolNames']
    })
  }
  ngOnInit() {
  }
  submitCredentials() {
    this.toolName = (this.toolName != "Others" ? this.toolName : this.toolNameOthers);
    this.userFormat = /^[a-zA-Z0-9 _.-]*$/;
    this.passwordFormat = /^(?=.*\d)(?=.*[a-z])(?=.*[A-Z])(?=.*[a-zA-Z]).{8,}$/;
    this.toolNameFormat = /^[a-zA-Z0-9 _.-]*/;
    if (this.userId.trim() == '') {
      alert('Please enter User ID');
      return;
    }
    if (!this.userFormat.test(String(this.userId.trim().toLowerCase()))) {
      alert("userId is invalid")
      return;
    }
    if (this.password.trim() == '') {
      alert('Please enter Password');
      return;
    }
    if (!this.passwordFormat.test(String(this.password.trim()))) {
      alert("password is invalid");
      return;
    }
    if (this.toolName.trim() == '') {
      alert('Please enter the ITSM Tool Name');
      return;
    }
    if (!this.toolNameFormat.test(String(this.toolName.trim().toLowerCase()))) {
      alert("toolname is invalid");
      return;
    }
    if (this.userId != '' && this.password != '' && this.toolName != '') {
      let document = {}
      document['UserID'] = this.userId.trim();
      document['Password'] = this.password.trim();
      document['ITSMToolName'] = this.toolName.trim();
      this.httpClient.post('/api/insertITSMDetails', [document], { responseType: 'text' })
        .subscribe(resp => {
          console.log(resp);
          this.showMessage = true;
          this.userId = '';
          this.password = '';
          this.toolName = '';
        });
    }
  }
}