/* Copyright 2022 Infosys Ltd.Use of this source code is governed by MIT license that can be found in the LICENSE file or athttps://opensource.org/licenses/MIT.*/
import { Component, Input, OnInit, EventEmitter, Output } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { NgbModal, NgbActiveModal, ModalDismissReasons } from '@ng-bootstrap/ng-bootstrap';
import { CloudData, CloudOptions } from 'angular-tag-cloud-module';
import { ViewEncapsulation } from '@angular/core';
import { delay } from 'q';
import { RequestOptions } from '@angular/http';
import { LogsComponent } from '../logs/logs.component'
@Component({
  selector: 'app-orchestrator-args-popup',
  templateUrl: './orchestrator-args-popup.component.html',
  styleUrls: ['./orchestrator-args-popup.component.scss']
})
export class OrchestratorArgsPopupComponent implements OnInit {
  @Input() dataToTakeAsInput: any;
  argList: any = {};
  closeResult: string;
  scriptStatus: boolean = false;
  argValue: any = {}
  @Output() emitData = new EventEmitter();
  auditLogs: any = []
  workflowDetails: any = {};
  argStatus: boolean = false;
  ngOnInit() {
    this.argList = this.dataToTakeAsInput["ScriptDetails"]["orchestrator_args_list"][0];
    this.workflowDetails = this.dataToTakeAsInput["ScriptDetails"];
  }
  constructor(private httpClient: HttpClient, private modalService: NgbModal, public activeModal: NgbActiveModal) {
  }
  open(content) {
    this.modalService.open(content, { ariaLabelledBy: 'modal-basic-title', size: "lg" }).result.then((result) => {
      this.closeResult = 'Closed with: ${result}';
    });
  }
  invoke_Orchestrator() {
    if (Object.keys(this.argList).length == Object.keys(this.argValue).length) {
      let formData = new FormData();
      formData.append('workflow_parameters', JSON.stringify(this.argValue));
      this.httpClient.post('/api/executeWorkFlow/' + this.workflowDetails['name'] + '/' + this.dataToTakeAsInput["IncidentNumber"], formData, { responseType: 'json' }).subscribe(data => {
        this.SaveResolutionDetails('orchestrator', this.workflowDetails['name'], 'success', 'Started Successfully.')
        this.httpClient.get('/api/getAuditLogs/' + this.dataToTakeAsInput["IncidentNumber"]).subscribe(data => {
          this.auditLogs = data;
          this.auditLogs.reverse()
          this.emitData.next(this.auditLogs);
          console.log(this.auditLogs)
        });
        alert("workflow started succesfully");
      }, err => {
        console.error('Could not execute script due to some error! Please try again later');
      });
    } else
      alert('Please provide value for all arguments');
  }
  SaveResolutionDetails(type: any, name: any, status: any, logs: any) {
    let formdata = new FormData()
    formdata.append('Number', this.dataToTakeAsInput["IncidentNumber"])
    formdata.append('Description', this.dataToTakeAsInput["Description"])
    formdata.append('Type', type)
    formdata.append('Name', name)
    formdata.append('Status', status)
    formdata.append('Logs', logs)
    this.httpClient.post('/api/SaveResolutionDetails', formdata, { responseType: 'text' }).subscribe(data => {
      //console.log(data)
    })
  }
}
