/* Copyright 2022 Infosys Ltd.Use of this source code is governed by MIT license that can be found in the LICENSE file or athttps://opensource.org/licenses/MIT.*/
import { Component, Input, OnInit, Output, EventEmitter, ViewChild, ElementRef } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { NgbModal, NgbActiveModal, ModalDismissReasons } from '@ng-bootstrap/ng-bootstrap';
import { CloudData, CloudOptions } from 'angular-tag-cloud-module';
import { ViewEncapsulation } from '@angular/core';
import { delay } from 'q';
import { RequestOptions } from '@angular/http';
import { LogsComponent } from '../logs/logs.component'
import { ArgsComponent } from '../arg-popup/arg-popup.component'
@Component({
  selector: 'app-diag-popup',
  templateUrl: './diag-popup.component.html',
  styleUrls: ['./diag-popup.component.css'],
  encapsulation: ViewEncapsulation.None
})
export class DiagComponent implements OnInit {
  @Input() dataToTakeAsInput: any;
  argList: any = []
  closeResult: string;
  objectKeys: any;
  logs = {}
  type: any;
  message: any;
  scriptStatus: boolean = false;
  row: any;
  auditLogs: any = []
  @Output() emitData = new EventEmitter();
  constructor(private httpClient: HttpClient, private modalService: NgbModal, public activeModal: NgbActiveModal) {
  }
  ngOnInit() {
    this.row = this.dataToTakeAsInput['Row']
    this.httpClient.get('/api/getDiagnosticScript/' + this.row['name']).subscribe(data => {
      this.argList = data
    })
  }
  provideArgs(diag_name: any) {
    const modalRef = this.modalService.open(ArgsComponent, { size: 'lg', windowClass: 'app-modal-window', backdrop: false });
    modalRef.componentInstance.emitData.subscribe(($e) => {
      this.auditLogs = $e;
      this.emitData.next(this.auditLogs)
    })
    let dataPassToChild: any = {};
    dataPassToChild['ScriptDetails'] = this.row;
    dataPassToChild['Type'] = 'diagnostic';
    dataPassToChild['DiagName'] = diag_name;
    (<ArgsComponent>modalRef.componentInstance).dataToTakeAsInput = dataPassToChild;
    modalRef.result.then((result) => {
      console.log(result);
    }).catch((result) => {
      console.log(result);
    });
  }
  closeAlert() {
    this.scriptStatus = false;
  }
  open(content) {
    this.modalService.open(content, { ariaLabelledBy: 'modal-basic-title', size: "lg" }).result.then((result) => {
      this.closeResult = 'Closed with: ${result}';
    });
  }
}
