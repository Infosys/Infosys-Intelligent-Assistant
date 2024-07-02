/* Copyright 2022 Infosys Ltd.Use of this source code is governed by MIT license that can be found in the LICENSE file or athttps://opensource.org/licenses/MIT.*/
import { Component, Input, OnInit } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { NgbModal, NgbActiveModal, ModalDismissReasons } from '@ng-bootstrap/ng-bootstrap';
import { CloudData, CloudOptions } from 'angular-tag-cloud-module';
import { ViewEncapsulation } from '@angular/core';
import { delay } from 'q';
import { RequestOptions } from '@angular/http';
@Component({
  selector: 'app-logs',
  templateUrl: './logs.component.html',
  styleUrls: ['./logs.component.css'],
  encapsulation: ViewEncapsulation.None
})
export class LogsComponent implements OnInit {
  @Input() dataToTakeAsInput: any;
  logsJson={}
  closeResult: string;
  objectKeys:any;
  constructor(private httpClient: HttpClient, private modalService: NgbModal, public  activeModal:  NgbActiveModal) {
  }
  ngOnInit() {
    this.logsJson=this.dataToTakeAsInput['Logs']
    this.objectKeys=Object.keys(this.logsJson)
  }
  open(content) {
    this.modalService.open(content, { ariaLabelledBy: 'modal-basic-title', size: "lg" }).result.then((result) => {
      this.closeResult = 'Closed with: ${result}';
    });
  }
}
