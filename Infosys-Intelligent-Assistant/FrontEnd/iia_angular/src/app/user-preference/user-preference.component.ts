/* Copyright 2022 Infosys Ltd.Use of this source code is governed by MIT license that can be found in the LICENSE file or athttps://opensource.org/licenses/MIT.*/
import { Component, OnInit, Input } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { NgForm } from '@angular/forms';
@Component({
  selector: 'user-preference',
  templateUrl: './user-preference.component.html',
  styleUrls: ['./user-preference.component.css']
})
export class UserPreferenceComponent implements OnInit {
  algorithmChosen: boolean = false;
  customerId: number = 1;
  predictedFieldsInformation: any = [];
  algorithmsInformation: any = [];
  accuracies: any = [];
  constructor(private httpClient: HttpClient) {
    this.showAlgorithms();
  }
  ngOnInit() {
  }
  ngDoCheck() {
  }
  showAlgorithms() {
    this.algorithmChosen = true;
    this.predictedFieldsInformation = [];
    this.algorithmsInformation = [];
    this.httpClient.get('/api/algorithms/' + this.customerId).subscribe(data => {
      this.predictedFieldsInformation = data['PredictedFields'];
      this.predictedFieldsInformation.forEach(predictedField => {
        this.algorithmsInformation.push(predictedField['Algorithms']);
      });
    })
  }
}