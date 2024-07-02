/* Copyright 2022 Infosys Ltd.Use of this source code is governed by MIT license that can be found in the LICENSE file or athttps://opensource.org/licenses/MIT.*/
import { Component, ViewEncapsulation } from '@angular/core';
import { HttpClient } from '@angular/common/http'
@Component({
  selector: 'app-image-analysis-details',
  templateUrl: './image-analysis-details.component.html',
  styleUrls: ['./image-analysis-details.component.css'],
})
export class imageAnalysisDetailsComponent {
  columnsSelected: any = [];
  newcolumnlst: any = [];
  saveSuccess: boolean = false;
  msg: string;
  msgClr: string;
  showMsgState: boolean = false;
  disableTeam: boolean = false;
  constructor(private httpClient: HttpClient) { }
  ngOnInit() {
    // to show previos  optionsselected from DB 
    this.httpClient.get('/api/imageAnalysis/getColumnNames').subscribe(data => {
      if (data['response'] != 'failure') {
        this.columnsSelected = data['response'];
      } else {
        console.warn('Could not get data from api!');
      }
    }, err => {
      console.error('Could not get data! ,' + err)
    });
  }
  saveColumnNames() {
    let data = this.columnsSelected;
    let temp_lst: any = [];
    for (let key in data) {
      this.newcolumnlst.push(data[key])
    }
    temp_lst = [];
    this.newcolumnlst.forEach(value => {
      if (typeof value != 'string') {
        temp_lst.push(value['value']);
      } else
        temp_lst.push(value);
    });
    this.httpClient.post('/api/saveimageAnalysisColumnNames', temp_lst, { responseType: 'text' }).subscribe(data => {
      if (data == 'success') {
        this.msg = 'Saved successfully!';
        this.msgClr = 'green';
        this.showMsgState = true;
        this.ngOnInit();
        this.newcolumnlst = [];
      } else {
        this.msgClr = 'red';
        this.msg = 'Could not Save!';
        this.ngOnInit();
      }
    }, err => {
      this.msgClr = 'red';
      this.msg = 'Could not Save due to some Error! Try again later';
      console.error('Could not save!, : ' + err);
    });
    this.showMsgState = true;
    temp_lst = [];
  }
  max_count() {
    if (this.columnsSelected.length == 5) {
      alert("max columns  limit reached ");
    }
  }
  addElement() {
    this.saveSuccess = false;
  }
}