/* Copyright 2022 Infosys Ltd.Use of this source code is governed by MIT license that can be found in the LICENSE file or athttps://opensource.org/licenses/MIT.*/
import { HttpClient } from "@angular/common/http";
import { Component, EventEmitter, Input, OnInit, Output, ViewEncapsulation } from "@angular/core";
import { NgbModal, NgbActiveModal, ModalDismissReasons } from '@ng-bootstrap/ng-bootstrap';
import { RpaPopupComponent } from "../rpa-popup/rpa-popup.component";
@Component({
  selector: 'app-rpa-diag-popup',
  templateUrl: './rpa-diag-popup.component.html',
  styleUrls: ['./rpa-diag-popup.component.scss'],
  encapsulation: ViewEncapsulation.None
})
export class RpaDiagPopupComponent implements OnInit {
  row: any;
  @Input() dataToTakeAsInput: any;
  argList: any = [];
  auditLogs: any = [];
  @Output() emitData = new EventEmitter();
  scriptStatus: boolean;
  closeResult: string;
  constructor(private httpClient: HttpClient, private modalService: NgbModal, public activeModal: NgbActiveModal) {
  }
  ngOnInit() {
    this.row = this.dataToTakeAsInput['Row']
    this.httpClient.get('/api/getDiagnosticRPA/' + this.row['name']).subscribe(data => {
      this.argList = data
    })
  }
  provideArgs(diag_name: any) {
    const modalRef = this.modalService.open(RpaPopupComponent, { size: 'lg', windowClass: 'app-modal-window', backdrop: false });
    modalRef.componentInstance.emitData.subscribe(($e) => {
      this.auditLogs = $e;
      this.emitData.next(this.auditLogs)
    })
    let dataPassToChild: any = {};
    dataPassToChild['ScriptDetails'] = this.row;
    dataPassToChild['Type'] = 'diagnostic';
    dataPassToChild['DiagName'] = diag_name;
    (<RpaPopupComponent>modalRef.componentInstance).dataToTakeAsInput = dataPassToChild;
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