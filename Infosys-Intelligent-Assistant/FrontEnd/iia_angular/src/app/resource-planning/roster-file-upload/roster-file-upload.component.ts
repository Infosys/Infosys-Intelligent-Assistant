/* Copyright 2022 Infosys Ltd.Use of this source code is governed by MIT license that can be found in the LICENSE file or athttps://opensource.org/licenses/MIT.*/
import { Component, ViewChild, OnInit, ElementRef } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { HttpErrorResponse } from '@angular/common/http';
import { Router } from '@angular/router';
import { NgbModal, NgbActiveModal, ModalDismissReasons } from '@ng-bootstrap/ng-bootstrap';
import { ValidationMessageComponent } from '../validation-message/validation-message.component'
@Component({
  selector: 'app-roster-file-upload',
  templateUrl: './roster-file-upload.component.html',
  styleUrls: ['./roster-file-upload.component.scss']
})
export class RosterFileUploadComponent implements OnInit {
  @ViewChild('roasterDetails') fileInput: ElementRef;
  loader: boolean;
  constructor(private httpService: HttpClient) { }
  ngOnInit() {
  }
  uploadMonthlyRoasterDetails() {
    this.loader = true;
    const fileBrowser = this.fileInput.nativeElement;
    if (fileBrowser.files && fileBrowser.files[0]) {
      const formData = new FormData();
      formData.append('roasterDetails', fileBrowser.files[0]);
      this.httpService.post('/api/uploadMonthlyRoasterDetails', formData).subscribe(data => {
        if (data['status'] != 'failure') {
          console.log("inside upload file roster..." + data['status']);
        } else {
          console.log('Oooops!!, data did not come from backend');
        }
        this.loader = false;
      }, err => {
        console.log(err);
        throw '';
      });
    } else {
      alert('Please choose the right file..!');
      this.loader = false;
    }
  }
}
