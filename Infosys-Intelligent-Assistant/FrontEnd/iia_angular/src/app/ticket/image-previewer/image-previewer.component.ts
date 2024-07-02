/* Copyright 2022 Infosys Ltd.Use of this source code is governed by MIT license that can be found in the LICENSE file or athttps://opensource.org/licenses/MIT.*/
import { Component, OnInit, Input } from '@angular/core';
import { NgbModal, NgbActiveModal, ModalDismissReasons } from '@ng-bootstrap/ng-bootstrap';
import { ImageViewerModule } from 'ngx-image-viewer'
import { ImageViewerConfig, CustomEvent } from 'ngx-image-viewer';
import { ViewEncapsulation } from '@angular/core';
declare var require: any
@Component({
  selector: 'app-image-previewer',
  templateUrl: './image-previewer.component.html',
  styleUrls: ['./image-previewer.component.css'],
  encapsulation: ViewEncapsulation.None
})
export class ImagePreviewerComponent implements OnInit {
  @Input() dataToTakeAsInput: any;
  number: string;
  constructor(private modalService: NgbModal, public activeModal: NgbActiveModal) { }
  images = [];
  config: ImageViewerConfig = { customBtns: [{ name: 'print', icon: 'fa fa-print' }, { name: 'link', icon: 'fa fa-link' }] };
  imageIndexOne = 0;
  ngOnInit() {
    this.images.push('assets/uploads/'+ this.dataToTakeAsInput['IncidentNumber']+'.PNG');
  }
}
