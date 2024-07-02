/* Copyright 2022 Infosys Ltd.Use of this source code is governed by MIT license that can be found in the LICENSE file or athttps://opensource.org/licenses/MIT.*/
//  import { Component, OnInit } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Component, OnInit, Input, ViewChild, ElementRef } from '@angular/core';
@Component({
  selector: 'app-clustering',
  templateUrl: './clustering.component.html',
  styleUrls: ['./clustering.component.scss']
})
export class ClusteringComponent implements OnInit {
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
  flag: boolean = false;
  constructor(private httpClient: HttpClient) {
  }
  ngOnInit() {
    this.httpClient.get('/api/getDatasetTeamNames/' + this.customerId).subscribe(data => {
      if (data['Teams'].length > 0) {
        this.datasetID = data['DatasetIDs'][0];
        this.category
      }
    });
  }
  uploadcsv() {
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
              alert("Data uploaded successfully");
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
  getTeams(customerId: number) {
    throw new Error('Method not implemented.');
  }
  cloudTypeChanged(dropdownvalue: any) {
    const num = Number(dropdownvalue);
    this.clusterchosen = num;
    this.seconddropdown.splice(0, this.seconddropdown.length)
    for (let i = 0; i < num; i++) {
      this.seconddropdown.push(i)
    }
  }
  category(dropdownvalue: any) {
    if (dropdownvalue == "description") {
      this.category1 = "description";
      this.selecttype1 = undefined;
      this.clusterchosen = undefined;
      this.secondchoosen = undefined;
    }
    else if (dropdownvalue == "short_description") {
      this.category1 = "short_description";
      this.selecttype1 = undefined;
      this.clusterchosen = undefined;
      this.secondchoosen = undefined;
    }
    else {
      this.category1 = "Description+Short description";
    }
  }
  initial_Bar_graph() {
    this.loading = true
    this.httpClient.get('/api/generateCluster/' + this.customerId + '/' + this.datasetID + '/' + this.category1, { responseType: "text" }).subscribe(data => {
      if (data == "Success") {
        this.loading = false
        this.flag = false
        this.selecttype1 = undefined;
        this.clusterchosen = undefined;
        this.secondchoosen = undefined;
      }
      else {
        alert("Selected category not in dataset")
        this.flag = true
        this.loading = false
        this.selecttype1 = undefined;
        this.clusterchosen = undefined;
        this.secondchoosen = undefined;
      }
    });
  }
  selecttype(dropdownvalue: any) {
    if (dropdownvalue == "Unigram") {
      this.selecttype1 = "Unigram";
    }
    else if (dropdownvalue == "Bigram") {
      this.selecttype1 = "Bigram";
    }
    else if (dropdownvalue == "Trigram") {
      this.selecttype1 = "Trigram";
    }
  }
  selectname(dropdownvalue: any) {
    console.log(dropdownvalue);
    this.secondchoosen = dropdownvalue;
  }
  handleClick() {
    this.loading = true
    if (this.category1 == undefined || this.clusterchosen == undefined || this.selecttype1 == undefined || this.secondchoosen == undefined) {
      alert("Please provide mandatory fields.")
      this.loading = false;
    } else {
      let sendData = {
        clusters: this.clusters,
        seconddropdown: this.seconddropdown,
        cloudtype: this.cloudType,
        category: this.category
      }
      this.httpClient.get('/api/generateWordCloud/' + this.clusterchosen + '/' + this.selecttype1 + '/' + this.secondchoosen + '/' + this.category1, { responseType: "text" }).subscribe(data => {
        if (data == "Success") {
          this.loading = false
          this.image_src = '/assets/video/PMA_Cluster_' + this.clusterchosen + '_' + this.selecttype1 + '_' + this.secondchoosen + '.png'
        } else {
          this.loading = false
        }
      });
    }
  }
  onChangeDisable() {
    if (this.category1 || this.cloudTypeChanged || this.clusters || this.seconddropdown) {
      this.currentlyDisabled = 'two';
    } else {
      this.currentlyDisabled = '';
    }
  }
}
function handleClick() {
  throw new Error('Function not implemented.');
}
function onChangeDisable() {
  throw new Error('Function not implemented.');
}
