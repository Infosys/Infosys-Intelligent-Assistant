/* Copyright 2022 Infosys Ltd.Use of this source code is governed by MIT license that can be found in the LICENSE file or athttps://opensource.org/licenses/MIT.*/
import { HttpClient } from '@angular/common/http';
import { Component, ElementRef, OnInit, ViewChild } from '@angular/core';
import { MatTabChangeEvent } from '@angular/material';
import { CalendarHeatmapComponent } from './calendar-heatmap/calendar-heatmap.component'
import { ClusteringComponent } from './clustering/clustering.component';
import { FileuploadComponent } from './fileupload/fileupload.component';
import { LineGraphComponent } from './line-graph/line-graph.component';
import { MonthlyDetailComponent } from './monthly-details/monthly-details.component';
import { PieAnalysisComponent } from './pie-analysis/pie-analysis.component';
import { PMAAssignementComponent } from './PMA-Assignment/PMA-Assignment.component';
import { WeightedMovingAverageComponent } from './weighted-moving-average/weighted-moving-average.component';
@Component({
  selector: 'app-PMA',
  templateUrl: './PMA.Component.html',
  styleUrls: ['./PMA.Component.css']
})
export class PMAComponent {
  @ViewChild('trainingData') fileInput: ElementRef;
  @ViewChild(CalendarHeatmapComponent) heatmap: CalendarHeatmapComponent
  @ViewChild(LineGraphComponent) lineComp: LineGraphComponent
  @ViewChild(PieAnalysisComponent) pieComp: PieAnalysisComponent
  @ViewChild(ClusteringComponent) clusterComp: ClusteringComponent
  @ViewChild(MonthlyDetailComponent) monthlyComp: MonthlyDetailComponent
  @ViewChild(PMAAssignementComponent) barComp: PMAAssignementComponent
  @ViewChild(WeightedMovingAverageComponent) weightComp: WeightedMovingAverageComponent
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
  index: number;
  index1: number = 0;
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
  tabChanged(tabChangeEvent: MatTabChangeEvent) {
    this.index1 = tabChangeEvent.index;
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
            this.teamID = parseInt(data.toString());;
            this.httpClient.get('/api/getDatasetDetails/' + this.customerId + "/" + this.datasetID).subscribe(data => {
              this.datasetName = data['name'];
              this.datasetCount = data['count'];
              temp = data['fields'];
              temp.forEach((attribute, index) => {
                this.attributeList.push({ "id": index, "Attribute": attribute });
              });
              this.uniqueFieldList = this.attributeList.slice(0);
              this.predictedDropdownList = this.attributeList.slice(0);
              let tarCol = [];
              this.httpClient.post('/api/updatePMATargetColumns', tarCol).subscribe(data => {
                if (data == "success") {
                }
              })
              alert("Data uploaded successfully. Please map the fields in Admin module >> PMA Details");
              this.heatmap.ngOnInit();
              this.pieComp.ngOnInit();
              this.lineComp.ngOnInit();
              this.clusterComp.ngOnInit();
              this.barComp.ngOnInit();
              this.monthlyComp.ngOnInit();
              this.weightComp.ngOnInit();
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