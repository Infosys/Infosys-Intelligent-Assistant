/* Copyright 2022 Infosys Ltd.Use of this source code is governed by MIT license that can be found in the LICENSE file or athttps://opensource.org/licenses/MIT.*/
import { Component, ElementRef, ViewChild, OnInit, Injectable } from '@angular/core';
import {HttpClient,HttpHeaders} from '@angular/common/http';
import { MatTableDataSource, MatPaginator, MatSort, MatPaginatorModule, MatTableModule } from '@angular/material';
import { FormBuilder, FormControl, FormArray, FormGroup, Validators } from '@angular/forms';
import { COMMA, ENTER } from '@angular/cdk/keycodes';
import { Observable } from 'rxjs';
export interface UserData {
    Selected: any;
    workflow_name: string;
    keyword_mapping: string[];
    associated_Tasks:string[];
    edit:string;
  }
@Component ({
    selector : 'app-BOT-imageanalysis',
    templateUrl : './BOT-imageanalysis.component.html',
    styleUrls : ['./BOT-imageanalysis.component.css']
})
export class BOTimageAnalysisComponent{
    dataSource: MatTableDataSource<UserData>;
    tempList: any;
    public scriptsInfo: UserData[] = [];
    @ViewChild(MatPaginator) paginator: MatPaginator;
    @ViewChild(MatSort) sort: MatSort;
    displayedColumns: string[] = ['scriptName','associatedTasks'];
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
    // public scriptsInfo: UserData[] = [];
    scripts = [];
    operation: any;
    // tempList: any
    closeResult: any;
    scriptsList: any = []
    disableEdit: boolean = true;
    constructor(private httpclient: HttpClient) {
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
        this.httpclient.get("/api/getImageApplicationFlow").subscribe(data => {
          this.tempList = []
          this.tempList = data
          this.tempList.forEach(element => {
           this.scriptsInfo.push({ Selected: false, workflow_name: element["workflow_name"],  keyword_mapping: element["keyword_mapping"],associated_Tasks: element["associated_tasks"],edit:'' })
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
          {
            count = count + 1;
            // element.Selected=false;
            // alert(element.Selected);
          }
        });
        if (count == 1)
          this.disableEdit = false;
        else
          this.disableEdit = true;
      }
      invokeBPMN() {        
        let hostname = "localhost"
        let port = 'Enter port name'
        var wrk='default'; 
        this.httpclient.get('/api/getConfigKey/bpmn_editor').subscribe(data=>{
            if (data['Status'] == 'Success') {              
              hostname = data['hostname']
              port = data['port']              
            }
            window.open('http://'+ hostname +':' + port + '/?name=' + wrk);
      }, err =>{
        window.open('http://'+ hostname +':' + port + '/?name=' + wrk);
    });
    }
      editWorkFlow(workflowNme) {
        let hostname = "localhost"
        let port = 'Enter port name'
        var wrk= workflowNme
        this.httpclient.get('/api/getConfigKey/bpmn_editor').subscribe(data=>{
            if (data['Status'] == 'Success') {              
              hostname = data['hostname']
              port = data['port']             
            }
            window.open('http://'+ hostname +':' + port + '/?name=' + wrk);
        }, err =>{
          window.open('http://'+ hostname +':' + port + '/?name=' + wrk);
      });
    }
      scriptsLoad() {
        this.workflowLoad();
      }          
        }
