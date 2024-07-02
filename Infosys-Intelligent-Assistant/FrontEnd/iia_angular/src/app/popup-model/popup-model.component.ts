/* Copyright 2022 Infosys Ltd.Use of this source code is governed by MIT license that can be found in the LICENSE file or athttps://opensource.org/licenses/MIT.*/
import { Component, OnInit } from '@angular/core';
import { NgbModal, NgbActiveModal, ModalDismissReasons } from '@ng-bootstrap/ng-bootstrap';
@Component({
  selector: 'app-popup-model',
  templateUrl: './popup-model.component.html',
  styleUrls: ['./popup-model.component.css']
})
export class PopupModelComponent implements OnInit {
  constructor(public activeModal: NgbActiveModal) { }
  ngOnInit() {
  }
  algorithmsInformation: any = [];
}
