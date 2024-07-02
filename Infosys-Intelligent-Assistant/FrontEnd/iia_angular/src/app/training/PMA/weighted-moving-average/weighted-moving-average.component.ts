/* Copyright 2022 Infosys Ltd.Use of this source code is governed by MIT license that can be found in the LICENSE file or athttps://opensource.org/licenses/MIT.*/
import { Component, OnInit } from '@angular/core';
import { HttpClient } from '@angular/common/http';
@Component({
  selector: 'app-weighted-moving-average',
  templateUrl: './weighted-moving-average.component.html',
  styleUrls: ['./weighted-moving-average.component.css']
})
export class WeightedMovingAverageComponent implements OnInit {
  selected_field_default: string;
  selected_value_default: any = [];
  selected_value: string = "";
  selected_group_list: any[];
  loading: boolean = false;
  temp_list: any;
  private customerId: number = 1;
  datasetID: number;
  show_graph: boolean = true;
  selected_names: any;
  field_name: string;
  field_list: any = []
  flag: boolean = false
  f: string = "False"
  weighted_moving_average_graph_path_src: string;
  constructor(private httpClient: HttpClient) { }
  ngOnInit() {
    this.httpClient.get('/api/getDatasetTeamNames/' + this.customerId).subscribe(data => {
      if (data['Teams'].length > 0) {
        this.datasetID = data['DatasetIDs'][0];
        this.getFieldList()
      }
    });
  }
  getGroupNameList(selected_col) {
    this.httpClient.get('/api/getSelctedColumnData/' + this.customerId + '/' + this.datasetID + "/" + selected_col, { responseType: 'json' }).subscribe(data => {
      if (data) {
        this.selected_group_list = []
        this.temp_list = data;
        for (let i = 0; i < this.temp_list.length; i++) {
          this.selected_group_list.push(this.temp_list[i]);
        }
      }
    });
  }
  default_moving_average_graph(selected_field, selected_value_default) {
    this.loading = true;
    let sendData = {
      selected_field: selected_field,
      selected_value_list: selected_value_default,
      flag: this.flag
    }
    this.httpClient.post('/api/WeightedMovingAverage', sendData, { responseType: "text" }).subscribe(data => {
      if (data == "Success") {
        this.loading = false
        if (this.flag) {
          this.f = "True"
        }
        else {
          this.f = "False"
        }
        this.weighted_moving_average_graph_path_src = '/assets/video/' + this.f + this.field_name + '_' + this.selected_value_default + '_weighted-moving-average.png';
      }
    });
  }
  WeightedAverage_typechanged(dropdown) {
    this.selected_names = dropdown.value
  }
  WeightedAverage_field_changed(dropdownvalue) {
    if (dropdownvalue != "") {
      this.field_name = dropdownvalue;
      this.getGroupNameList(this.field_name)
    }
  }
  getFieldList() {
    this.httpClient.get('/api/barcategoryname/' + this.customerId + '/' + this.datasetID, { responseType: 'json' }).subscribe(data => {
      if (data) {
        this.temp_list = data;
        for (let i = 0; i < this.temp_list.length; i++) {
          this.field_list.push(this.temp_list[i]);
        }
      }
    });
  }
  handleClick() {
    this.loading = true
    if (this.field_name == undefined || this.selected_names == undefined) {
      alert("Please provide mandatory fields")
      this.loading = false;
    } else {
      let sendData = {
        selected_field: this.field_name,
        selected_value_list: this.selected_names,
        flag: this.flag
      }
      this.httpClient.post('/api/WeightedMovingAverage', sendData, { responseType: "text" }).subscribe(data => {
        if (data == "Success") {
          this.loading = false
          if (this.flag) {
            this.f = "True"
          }
          else {
            this.f = "False"
          }
          this.weighted_moving_average_graph_path_src = '/assets/video/' + this.f + this.field_name + '_' + this.selected_names.join("_") + '_weighted-moving-average.png';
        }
      });
    }
  }
  ComparisionCheckBox(e) {
    this.flag = e.target.checked
  }
}
