/* Copyright 2022 Infosys Ltd.Use of this source code is governed by MIT license that can be found in the LICENSE file or athttps://opensource.org/licenses/MIT.*/
import { Component, Input, OnInit } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { NgbModal, NgbActiveModal, ModalDismissReasons } from '@ng-bootstrap/ng-bootstrap';
import { CloudData, CloudOptions } from 'angular-tag-cloud-module';
import { ViewEncapsulation } from '@angular/core';
@Component({
  selector: 'app-warning-popup',
  templateUrl: './warning-popup.component.html',
  styleUrls: ['./warning-popup.component.scss'],
  encapsulation: ViewEncapsulation.None
})
export class WarningPopupComponent implements OnInit {
  @Input() dataToTakeAsInput: any;
  closeResult: string;
  constructor(private httpClient: HttpClient, private modalService: NgbModal, public  activeModal:  NgbActiveModal) { }
  ngOnInit() {
  }
  open(content) {
    this.modalService.open(content, { ariaLabelledBy: 'modal-basic-title', size: "lg" }).result.then((result) => {
      this.closeResult = 'Closed with: ${result}';
    });
  }
}
