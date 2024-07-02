/* Copyright 2022 Infosys Ltd.Use of this source code is governed by MIT license that can be found in the LICENSE file or athttps://opensource.org/licenses/MIT.*/
import { FormBuilder, FormControl, FormArray, FormGroup, Validators } from '@angular/forms';
import { HttpClient, HttpClientModule } from '@angular/common/http';
import { ResponseType } from '@angular/http';
import { text, template, element } from '@angular/core/src/render3';
import { COMMA, ENTER } from '@angular/cdk/keycodes';
import { Component, ElementRef, ViewChild, OnInit, Injectable } from '@angular/core';
import { MatAutocompleteSelectedEvent, MatChipInputEvent, MatAutocomplete } from '@angular/material';
import { Observable } from 'rxjs';
import { map, startWith } from 'rxjs/operators';
import { coerceNumberProperty } from '@angular/cdk/coercion'
import { MatTableDataSource, MatPaginator, MatSort, MatPaginatorModule, MatTableModule } from '@angular/material';
import { CreateScriptComponent } from '../create-script/create-script.component'
import { NgbModal, NgbActiveModal, ModalDismissReasons } from '@ng-bootstrap/ng-bootstrap';
export interface UserData {
  Selected: any;
  workflow_name: string;
  keyword_mapping: string[];
}
@Component({
  selector: 'app-workflow',
  templateUrl: './workflow.component.html',
  styleUrls: ['./workflow.component.css']
})
export class WorkflowComponent implements OnInit {
  displayedColumns: string[] = ['Selected', 'scriptName', 'keyword'];
  dataSource: MatTableDataSource<UserData>;
  @ViewChild(MatPaginator) paginator: MatPaginator;
  @ViewChild(MatSort) sort: MatSort;
  selectedAll: any;
  updation: boolean;
  addition: boolean = true;
  removal: boolean;
  visible = true;
  selectable = true;
  removable = true;
  addOnBlur = true;
  separatorKeysCodes: number[] = [ENTER, COMMA];
  keywordCtrl = new FormControl();
  filteredKeywords: Observable<string[]>;
  deploymentStatus: boolean;
  scriptName: string = "";
  args: boolean;
  sources: any[] = ["iOps", "Local"];
  selectedEnvironment: string = "";
  autoTicks = false;
  invert = false;
  showTicks = false;
  thumbLabel = false;
  value = 0;
  vertical = false;
  argumentCtrl = new FormControl();
  filteredArguments: Observable<string[]>;
  public scriptsInfo: UserData[] = [];
  scripts = [];
  operation: any;
  tempList: any
  closeResult: any;
  scriptsList: any = []
  disableEdit: boolean = true;
  saveSuccess: boolean;
  constructor(private httpClient: HttpClient, private modalService: NgbModal) {
  }
  ngOnInit() {
    this.workflowLoad();
  }
  applyFilter(filterValue: string) {
    this.dataSource.filter = filterValue.trim().toLowerCase();
    if (this.dataSource.paginator) {
      this.dataSource.paginator.firstPage();
    }
  }
  workflowLoad() {
    this.scriptsInfo = []
    this.httpClient.get("/api/getworkflow").subscribe(data => {
      this.tempList = []
      this.tempList = data
      this.tempList.forEach(element => {
        this.scriptsInfo.push({ Selected: false, workflow_name: element["workflow_name"], keyword_mapping: element["keyword_mapping"] })
      });
      // Assign the data to the data source for the table to render
      this.dataSource = new MatTableDataSource(this.scriptsInfo)
      this.dataSource.paginator = this.paginator;
      this.dataSource.sort = this.sort;
    })
  }
  private selectAll() {
    this.scriptsInfo.forEach((item, index) => {
      item.Selected = this.selectedAll;
    });
    this.checkIfAllSelected();
  }
  private checkIfAllSelected() {
    let count = 0;
    this.selectedAll = this.scriptsInfo.every(function (item: any) {
      return item.Selected == true;
    });
    this.dataSource.data.forEach(element => {
      if (element.Selected == true)
        count = count + 1;
    });
    if (count == 1)
      this.disableEdit = false;
    else
      this.disableEdit = true;
  }
  save() {
    this.httpClient.post('/api/saveworkflowkeywords', this.dataSource.data, { responseType: 'text' }).subscribe(data => {
      alert(data)
      this.workflowLoad()
    }, err => {
    });
  }
  invokeBPMN() {
    let hostname = "localhost"
    let port = '' // Enter port number
    var wrk = 'default';
    this.httpClient.get('/api/getConfigKey/bpmn_editor_standard').subscribe(data => {
      console.log(data)
      if (data['Status'] == 'Success') {
        hostname = data['hostname']
        port = data['port']
        console.log(port)
      }
      window.open('http://' + hostname + ':' + port + '/?name=' + wrk);
    }, err => {
      window.open('http://' + hostname + ':' + port + '/?name=' + wrk);
    });
  }
  editWorkFlow() {
    let workflowNme;
    this.dataSource.data.forEach(element => {
      if (element.Selected) {
        // temp[this.dataSource.data.indexOf(element)]=element;
        workflowNme = element.workflow_name;
      }
    });
    let hostname = "localhost"
    let port = '' // Enter Port number
    var wrk = workflowNme
    this.httpClient.get('/api/getConfigKey/bpmn_editor_standard').subscribe(data => {
      console.log(data)
      if (data['Status'] == 'Success') {
        hostname = data['hostname']
        port = data['port']
      }
      window.open('http://' + hostname + ':' + port + '/?name=' + wrk);
    }, err => {
      window.open('http://' + hostname + ':' + port + '/?name=' + wrk);
    });
  }
  addWorkflow() {
    this.saveSuccess = false;
  }
  scriptsLoad() {
    this.workflowLoad();
  }
}
