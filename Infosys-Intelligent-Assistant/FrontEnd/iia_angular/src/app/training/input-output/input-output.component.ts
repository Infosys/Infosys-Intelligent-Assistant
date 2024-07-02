/* Copyright 2022 Infosys Ltd.Use of this source code is governed by MIT license that can be found in the LICENSE file or athttps://opensource.org/licenses/MIT.*/
import { Component, OnInit, Input, ViewChild, ElementRef, Output, EventEmitter} from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { NgForm } from '@angular/forms';
import { Router } from '@angular/router';
@Component({
  selector: 'input-output',
  templateUrl: './input-output.component.html',
  styleUrls: ['./input-output.component.css']
})
export class InputOutputComponent implements OnInit {
  @Input() customerId: number;
  @Input() attributeList = [];
  @Input() datasetID: number;
  trainingId: number;
  inputDropdownList = [];
  predictedDropdownList = [];
  selectedInputFields = [];
  selectedPredictedFields = [];
  predictedDropdownSettings = {};
  inputDropdownSettings = {};
  fieldsToBeSaved = [];
  saveSuccess: boolean = false;
  approvedAlgorithms: boolean = false;
  loading: boolean = false;
  constructor(private httpClient: HttpClient, private router: Router) {
  }
  ngOnInit() {
  }
  ngOnChange() {
    this.selectedPredictedFields = [];
    this.selectedInputFields = [];
  }
}