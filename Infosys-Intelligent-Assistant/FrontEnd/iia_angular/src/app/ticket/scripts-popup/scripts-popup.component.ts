/* Copyright 2022 Infosys Ltd.Use of this source code is governed by MIT license that can be found in the LICENSE file or athttps://opensource.org/licenses/MIT.*/
import { Component, Input, OnInit } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { NgbModal, NgbActiveModal, ModalDismissReasons } from '@ng-bootstrap/ng-bootstrap';
import { CloudData, CloudOptions } from 'angular-tag-cloud-module';
import { ViewEncapsulation } from '@angular/core';
import { delay } from 'q';
import { RequestOptions } from '@angular/http';
import { LogsComponent } from '../logs/logs.component'
@Component({
  selector: 'app-scripts-popup',
  templateUrl: './scripts-popup.component.html',
  styleUrls: ['./scripts-popup.component.scss'],
  encapsulation: ViewEncapsulation.None
})
export class ScriptsPopupComponent implements OnInit {
  @Input() dataToTakeAsInput: any;
  scriptStatus1: boolean;
  closeResult: string;
  header: string;
  tempArray: any = [];
  scriptsEnable = false;
  sopsEnable = false;
  rpasEnable = false;
  jobsEnable = false;
  iopsEnable = false;
  scriptStatus: boolean;
  message: string;
  type: string;
  selectedValues: string[];
  ScriptOptions = new Array<CheckboxItem>();
  SOPSOptions = new Array<CheckboxItem>();
  RPAOptions = new Array<CheckboxItem>();
  JobsOptions = new Array<CheckboxItem>();
  IopsOptions = new Array<CheckboxItem>();
  IopsHistoricalOptions = new Array<CheckboxItem>();
  checkedOptions1: any = [];
  checkedOptions2: any = [];
  checkedOptions3: any = [];
  checkedOptions4: any = [];
  checkedOptions5: any = [];
  checkedOptions6: any = [];
  scriptsJson1: any;
  scriptsJson2: any;
  args: boolean;
  arguments1: any = [];
  arguments2: any = [];
  argumentList1 = {};
  argumentList2 = {};
  argValue: string;
  logs = {};
  emptyargumentScrips1: any = []
  emptyargumentScrips2: any = []
  mappedShowHide: boolean = true;
  historicalShowHide: boolean = false;
  envList = ['Local']
  selectedEnv = 'Local'
  IopsRecords = [];
  IopsHistoricalRecords = []
  ScriptRecords = [
    { id: 1, name: "Script 1" },
    { id: 2, name: "Script 2" },
    { id: 3, name: "Script 3" },
    { id: 4, name: "Script 4" }
  ];
  SOPSRecords = [
    { id: 11, name: "SOP 1" },
    { id: 12, name: "SOP 2" },
    { id: 13, name: "SOP 3" },
    { id: 14, name: "SOP 4" }
  ];
  RPARecords = [
    { id: 21, name: "DemoMailProcess" }
  ];
  JobsRecords = [
    { id: 31, name: "Jobs 1" },
    { id: 32, name: "Jobs 2" },
    { id: 33, name: "Jobs 3" },
    { id: 34, name: "Jobs 4" }
  ];
  constructor(private httpClient: HttpClient, private modalService: NgbModal, public activeModal: NgbActiveModal) {
  }
  ngOnInit() {
    console.log(this.dataToTakeAsInput['tabName'])
    let tempList: any = []
    this.httpClient.get("/api/getEnvironments").subscribe(data => {
      tempList = data
      tempList.forEach(element => {
        this.envList.push(element['name'])
      });
      console.log(this.envList)
    })
    this.ScriptOptions = this.ScriptRecords.map(x => new CheckboxItem(x.id, x.name));
    this.SOPSOptions = this.SOPSRecords.map(x => new CheckboxItem(x.id, x.name));
    this.RPAOptions = this.RPARecords.map(x => new CheckboxItem(x.id, x.name));
    this.JobsOptions = this.JobsRecords.map(x => new CheckboxItem(x.id, x.name));
    this.IopsOptions = this.IopsRecords.map(x => new CheckboxItem(x.id, x.name));
    if (this.dataToTakeAsInput['tabName'] == 'scripts') {
      this.header = "Invoke Scripts";
      this.scriptsEnable = true;
      this.sopsEnable = false;
      this.rpasEnable = false;
      this.jobsEnable = false;
      this.iopsEnable = false;
    }
    if (this.dataToTakeAsInput['tabName'] == 'sops') {
      this.header = "Automated SOP's";
      this.scriptsEnable = false;
      this.sopsEnable = true;
      this.rpasEnable = false;
      this.jobsEnable = false;
      this.iopsEnable = false;
    }
    if (this.dataToTakeAsInput['tabName'] == 'rpa') {
      this.header = "Invoke RPA's";
      this.scriptsEnable = false;
      this.sopsEnable = false;
      this.rpasEnable = true;
      this.jobsEnable = false;
      this.iopsEnable = false;
    }
    if (this.dataToTakeAsInput['tabName'] == 'batch') {
      this.header = "Batch Job's";
      this.scriptsEnable = false;
      this.sopsEnable = false;
      this.rpasEnable = false;
      this.jobsEnable = true;
      this.iopsEnable = false;
    }
    if (this.dataToTakeAsInput['tabName'] == 'iops') {
      this.httpClient.get("/api/getTopFiveScripts").subscribe(data => {
        this.tempArray = data;
        let temp = 40;
        this.tempArray.forEach(element => {
          this.IopsRecords.push({ id: 41 + this.tempArray.indexOf(element), name: element['scriptName'] })
        });
        this.IopsOptions = this.IopsRecords.map(x => new CheckboxItem(x.id, x.name));
        this.httpClient.get('/api/getScripts').subscribe(data => {
          this.scriptsJson1 = data;
          for (let j of this.tempArray) {
            for (let i of this.scriptsJson1) {
              if (j == i["scriptName"]) {
                if (i['argument'].length == 0) {
                  this.emptyargumentScrips1.push(i['scriptName'])
                }
                this.arguments1.push(i["argument"])
              }
            }
          }
          console.log(this.arguments1)
        })
      })
      this.header = "Scripts";
      this.scriptsEnable = false;
      this.sopsEnable = false;
      this.rpasEnable = false;
      this.jobsEnable = false;
      this.iopsEnable = true;
    }
    if (this.dataToTakeAsInput['tabName'] == 'workflow') {
      this.header = "Workflows";
      this.httpClient.get("/api/getworkflow").subscribe(data => {
      });
    }
  }
  open(content) {
    this.modalService.open(content, { ariaLabelledBy: 'modal-basic-title', size: "lg" }).result.then((result) => {
      this.closeResult = 'Closed with: ${result}';
    });
  }
  onToggleScripts() {
    this.checkedOptions1 = this.ScriptOptions.filter(x => x.checked);
  }
  onToggleSOPS() {
    this.checkedOptions2 = this.SOPSOptions.filter(x => x.checked);
  }
  onToggleRPA() {
    this.checkedOptions3 = this.RPAOptions.filter(x => x.checked);
  }
  onToggleJobs() {
    this.checkedOptions4 = this.JobsOptions.filter(x => x.checked);
  }
  onToggleIops() {
    this.checkedOptions5 = this.IopsOptions.filter(x => x.checked);
  }
  onToggleHistoricalIops() {
    this.checkedOptions6 = this.IopsHistoricalOptions.filter(x => x.checked);
  }
  wait(ms: number) {
    var start = new Date().getTime();
    var end = start;
    while (end < start + ms) {
      end = new Date().getTime();
    }
  }
  invokeScripts() {
  }
  invokeBatch() {
    this.logs = {}
    for (var item of this.checkedOptions4) {
      this.httpClient.get('/api/executeBatch/' + item["label"], { responseType: 'text' }).subscribe(data => {
        this.logs[item["label"]] = data;
        if (this.checkedOptions4.indexOf(item) + 1 == this.checkedOptions4.length) {
          this.type = 'success';
          this.message = "Operation Completed";
          this.scriptStatus = true;
        }
        if (data == 'success') {
          this.SaveResolutionDetails('job', item['label'], 'success', 'Running job : ' + data)
        } else {
          this.SaveResolutionDetails('job', item['label'], 'failure', 'Running job : ' + data)
        }
      }, err => {
        this.logs[item["label"]] = err;
        if (this.checkedOptions4.indexOf(item) + 1 == this.checkedOptions4.length) {
          this.type = 'success';
          this.message = "Operation Completed";
          this.scriptStatus = true;
        }
      });
    }
  }
  invokeRPA() {
    let temp: any = []
    this.checkedOptions3.forEach(element => {
      this.type = 'success';
      this.message = "Running...";
      this.scriptStatus1 = true;
      this.httpClient.get("/api/executeRPA/" + element["label"], { responseType: 'json' }).subscribe(data => {
        this.scriptStatus1 = false
        this.logs[element["label"]] = data
        temp = data
        this.type = 'success';
        this.message = "Operation Completed";
        this.scriptStatus = true;
        if (temp.includes('Job completed')) {
          this.SaveResolutionDetails('rpa', element["label"], 'success', 'Running rpa : ' + data)
        } else {
          this.SaveResolutionDetails('rpa', element["label"], 'failure', 'Running rpa : ' + data)
        }
      })
    });
  }
  SaveResolutionDetails(type: any, name: any, status: any, logs: any) {
    let formdata = new FormData()
    formdata.append('Number', this.dataToTakeAsInput["IncidentNumber"])
    formdata.append('Description', this.dataToTakeAsInput["Description"])
    formdata.append('Type', type)
    formdata.append('Name', name)
    formdata.append('Status', status)
    formdata.append('Logs', logs)
    this.httpClient.post('/api/SaveResolutionDetails', formdata, { responseType: 'text' }).subscribe(data => {
      console.log(data)
    })
  }
  argumentValue1(scriptName: any, argumentName: any, event) {
    let temp = {}
    if (this.argumentList1[scriptName] != null) {
      temp = this.argumentList1[scriptName]
    }
    temp[argumentName] = event.target.value;
    this.argumentList1[scriptName] = temp
  }
  argumentValue2(scriptName: any, argumentName: any, event) {
    let temp = {}
    if (this.argumentList2[scriptName] != null) {
      temp = this.argumentList2[scriptName]
    }
    temp[argumentName] = event.target.value;
    this.argumentList2[scriptName] = temp
  }
  invokeIops(value: any) {
    let checkedOptions: any;
    if (value == 'mapped') {
      checkedOptions = this.checkedOptions5
    } else {
      checkedOptions = this.checkedOptions6
    }
    this.logs = {};
    checkedOptions.forEach(item => {
      let formData = new FormData();
      formData.append('ScriptName', item["label"]);
      formData.append('Environment', this.selectedEnv)
      formData.append('Type', 'main')
      this.httpClient.post("/api/invokeIopsScripts", formData, { responseType: 'text' }).subscribe(data => {
        this.logs[item["label"]] = data;
        if (checkedOptions.indexOf(item) + 1 == checkedOptions.length) {
          this.type = 'success';
          this.message = "Operation Completed";
          this.scriptStatus = true;
        }
        if (!(data.toLowerCase().includes('exception')) && !(data.toLowerCase().includes('err')) && !(data.toLowerCase().includes('error')) && !(data.toLowerCase().includes('access denied'))) {
          this.SaveResolutionDetails('script', item["label"], 'success', 'Running Script : ' + data)
        } else {
          this.SaveResolutionDetails('script', item["label"], 'failure', 'Running Script : ' + data)
        }
      })
    })
  }
  scriptsTabChange(value: any) {
    if (value == "historical") {
      this.historicalShowHide = true;
      this.mappedShowHide = false;
    } else {
      this.historicalShowHide = false;
      this.mappedShowHide = true;
    }
  }
  showLogs(value: any) {
    console.log(value)
    const modalRef = this.modalService.open(LogsComponent, { size: 'lg', backdrop: false });
    let dataPassToChild: any = {};
    dataPassToChild['Logs'] = this.logs;
    (<LogsComponent>modalRef.componentInstance).dataToTakeAsInput = dataPassToChild;
    modalRef.result.then((result) => {
      console.log(result);
    }).catch((result) => {
      console.log(result);
    });
  }
  closeAlert() {
    this.scriptStatus = false;
  }
}
export class CheckboxItem {
  value: string;
  label: string;
  checked: boolean;
  constructor(value: any, label: any, checked?: boolean) {
    this.value = value;
    this.label = label;
    this.checked = checked ? checked : false;
  }
}
