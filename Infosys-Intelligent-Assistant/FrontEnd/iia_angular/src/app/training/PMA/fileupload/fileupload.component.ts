/* Copyright 2022 Infosys Ltd.Use of this source code is governed by MIT license that can be found in the LICENSE file or athttps://opensource.org/licenses/MIT.*/
// import { Component, OnInit } from '@angular/core';
import { Component, OnInit, Input, ViewChild, ElementRef } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { CalendarHeatmapComponent } from '../calendar-heatmap/calendar-heatmap.component';
@Component({
  selector: 'app-fileupload',
  templateUrl: './fileupload.component.html',
  styleUrls: ['./fileupload.component.scss']
})
export class FileuploadComponent implements OnInit {
  private heatMapComp: CalendarHeatmapComponent
  @ViewChild('trainingData') fileInput: ElementRef;
  cloudType: string;
  selected_field_default: string = 'Description';
  clusters: any = [2, 3, 4, 5, 6, 7, 8, 9, 10]
  clusterchoice: any = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
  seconddropdown: any = []
  variable: any;
  selected_names: any;
  loading: boolean;
  category1: string;
  category2: string = 'Description';
  currentlyDisabled: string;
  image_src: string;
  image_list: Array<String> = [];
  selecttype1: string;
  private customerId: number = 1;
  datasetID: number;
  selected_group_list: any[];
  temp_list: any;
  shahid: any;
  clusterchosen: any;
  secondchoosen: any;
  http: any;
  datasetEdited: boolean;
  datasetDeleted: boolean;
  datasetExists: boolean;
  uploadTrainingSuccess: boolean;
  attributeList: any[];
  postResult: string;
  teamID: number;
  selectedTeam: string;
  datasetName: any;
  datasetCount: any;
  uniqueFieldList: any[];
  predictedDropdownList: any[];
  constructor(private httpClient: HttpClient) {
  }
  ngOnInit() {
    this.httpClient.get('/api/getDatasetTeamNames/' + this.customerId).subscribe(data => {
      if (data['Teams'].length > 0) {
        this.datasetID = data['DatasetIDs'][0];
        this.uploadcsv()
      }
    });
  }
  uploadcsv() {
    this.loading = true;
    this.datasetDeleted = false;
    this.datasetEdited = false;
    this.datasetExists = false;
    this.uploadTrainingSuccess = false;
    this.attributeList = [];
    const fileBrowser = this.fileInput.nativeElement;
    let temp = [];
    if (fileBrowser.files && fileBrowser.files[0]) {
      this.loading = true;
      const formData = new FormData();
      formData.append('trainingData', fileBrowser.files[0]);
      this.httpClient.post('/api/uploadClusteringdata/' + this.customerId + "/" + this.datasetID, formData, { responseType: 'text' })
        .subscribe(data => {
          if (data == "success") {
            this.loading = false;
            this.uploadTrainingSuccess = true;
            this.datasetExists = true;
            this.postResult = 'Training data uploaded successfully!';
            this.teamID = parseInt(data.toString());
            this.httpClient.get('/api/getDatasetDetails/' + this.customerId + "/" + this.datasetID).subscribe(data => {
              this.datasetName = data['name'];
              this.datasetCount = data['count'];
              temp = data['fields'];
              temp.forEach((attribute, index) => {
                this.attributeList.push({ "id": index, "Attribute": attribute });
              });
              this.uniqueFieldList = this.attributeList.slice(0);
              this.predictedDropdownList = this.attributeList.slice(0);
              alert("Data uploaded successfully");
              this.heatMapComp.ngOnInit();
            },
              err => {
                this.loading = false;
                console.log(err);
                throw "";
              });
          } else {
            this.loading = false;
            alert("couldn't upload the file! please try again");
          }
        });
    }
  }
}
