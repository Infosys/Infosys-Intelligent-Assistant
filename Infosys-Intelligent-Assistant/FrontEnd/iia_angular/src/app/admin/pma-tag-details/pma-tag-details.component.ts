/* Copyright 2022 Infosys Ltd.Use of this source code is governed by MIT license that can be found in the LICENSE file or athttps://opensource.org/licenses/MIT.*/
// ***********************************************
import { Component, ViewEncapsulation } from '@angular/core';
import { HttpClient } from '@angular/common/http'
import { listener } from '../../../../node_modules/@angular/core/src/render3';
export interface ColumnNames {
  column?;
}
@Component({
  selector: 'app-pma-tag-details',
  templateUrl: './pma-tag-details.component.html',
  styleUrls: ['./pma-tag-details.component.css'],
  encapsulation: ViewEncapsulation.None
})
export class PMATagDetailsComponent {
  sourceColumns: ColumnNames[] = [];
  targetColumns: ColumnNames[] = [];
  showMessage: boolean;
  color: any;
  message: any;
  selectedName: any;
  itsmName: any;
  Lst: any = [];
  constructor(private httpClient: HttpClient) { }
  ngOnInit() {
    this.getSourceColumns();
  }
  getSourceColumns() {
    this.httpClient.get('/api/getSourceTargetColumns').subscribe(data => {
      data['sourceColumns'].forEach(element => {
        this.sourceColumns.push({ 'column': element });
      });
      data['targetColumns'].forEach(element => {
        this.targetColumns.push({ 'column': element });
      });
    }, err => {
      console.log('Could not get source columns');
    });
  }
  submit() {
    let tarcol = [];
    this.targetColumns.forEach(element => {
      tarcol.push(element['column']);
    });
    this.httpClient.post('/api/updatePMATargetColumns', tarcol, { responseType: 'text' }).subscribe(data => {
      this.showMessage = true;
      if (data == 'success') {
        this.color = 'green'
        this.message = 'Saved Successfully!';
      } else {
        this.color = 'red'
        this.message = 'Could not save! Try again';
      }
    }, err => {
      console.log('Could not update the selected columns in the database');
    });
  }
}