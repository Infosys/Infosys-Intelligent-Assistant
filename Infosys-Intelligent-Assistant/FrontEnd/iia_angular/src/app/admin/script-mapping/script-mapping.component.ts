/* Copyright 2022 Infosys Ltd.Use of this source code is governed by MIT license that can be found in the LICENSE file or athttps://opensource.org/licenses/MIT.*/
import { FormBuilder, FormControl, FormArray, FormGroup, Validators } from '@angular/forms';
import { HttpClient, HttpClientModule } from '@angular/common/http';
import { ResponseType } from '@angular/http';
import { text, template } from '@angular/core/src/render3';
import { COMMA, ENTER } from '@angular/cdk/keycodes';
import { Component, ElementRef, ViewChild, OnInit, Injectable } from '@angular/core';
import { MatAutocompleteSelectedEvent, MatChipInputEvent, MatAutocomplete } from '@angular/material';
import { Observable } from 'rxjs';
import { map, startWith } from 'rxjs/operators';
import { coerceNumberProperty } from '@angular/cdk/coercion'
import { MatTableDataSource, MatPaginator, MatSort, MatPaginatorModule, MatTableModule } from '@angular/material';
import { CreateScriptComponent } from '../create-script/create-script.component'
import { NgbModal, NgbActiveModal, ModalDismissReasons } from '@ng-bootstrap/ng-bootstrap';
import { element } from 'protractor';
export interface UserData {
  Selected: any;
  scriptName: string;
  keyword: string[];
}
@Component({
  selector: 'app-scripts-mapping',
  templateUrl: './script-mapping.component.html',
  styleUrls: ['./script-mapping.component.css']
})
export class ScriptsMappingComponent implements OnInit {
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
  //   argStatus:boolean;
  invert = false;
  showTicks = false;
  thumbLabel = false;
  value = 0;
  vertical = false;
  argumentCtrl = new FormControl();
  filteredArguments: Observable<string[]>;
  //   disabledList: any[] = []
  public scriptsInfo: UserData[] = [];
  scripts = [];
  operation: any;
  tempList: any
  closeResult: any;
  scriptsList: any = []
  constructor(private httpClient: HttpClient, private modalService: NgbModal) {
  }
  ngOnInit() {
    this.scriptsLoad();
    this.configLoad();
    //   this.getScriptNames()
  }
  applyFilter(filterValue: string) {
    this.dataSource.filter = filterValue.trim().toLowerCase();
    if (this.dataSource.paginator) {
      this.dataSource.paginator.firstPage();
    }
  }
  scriptsLoad() {
    this.scriptsInfo = []
    this.httpClient.get("/api/getAllIopsScripts").subscribe(data => {
      this.tempList = []
      this.tempList = data
      this.tempList.forEach(element => {
        this.scriptsInfo.push({ Selected: false, scriptName: element["scriptName"], keyword: element["keyword"] })
      });
      // Assign the data to the data source for the table to render
      this.dataSource = new MatTableDataSource(this.scriptsInfo)
      this.dataSource.paginator = this.paginator;
      this.dataSource.sort = this.sort;
    })
  }
  configLoad() {
    this.scriptsInfo = []
    this.httpClient.get("/api/getAllRPAConfig1").subscribe(data => {
      this.tempList = []
      this.tempList = data
      this.tempList.forEach(element => {
        this.scriptsInfo.push({ Selected: false, scriptName: element["scriptName"], keyword: element["keyword"] })
      });
      this.dataSource = new MatTableDataSource(this.scriptsInfo)
      this.dataSource.paginator = this.paginator;
      this.dataSource.sort = this.sort;
    })
  }
  private selectAll() {
    this.scriptsInfo.forEach((item, index) => {
      item.Selected = this.selectedAll;
    });
  }
  private checkIfAllSelected() {
    this.selectedAll = this.scriptsInfo.every(function (item: any) {
      return item.Selected == true;
    });
  }
  save1() {
    let temp: any = []
    let tempscr: any = []
    let tempCon: any = []
    this.httpClient.get("/api/getAllIopsScripts").subscribe(data => {
      temp = data;
    });
    this.scripts = []
    let selectedScripts = []
    let allScripts = []
    let duplicateStatus = true;
    this.dataSource.data.forEach(element => {
      if (element.Selected) {
        temp[this.dataSource.data.indexOf(element)] = element;
      }
    });
    let temp1 = []
    temp.forEach(element => {
      if (element.Selected) {
        if (element['keyword'].length == 0) {
          element["keyword"] = []
        } else if (element["keyword"] instanceof Array) {
          element["keyword"] = element["keyword"]
        } else {
          element["keyword"] = element["keyword"].split(',')
        }
        temp1.push(element)
        this.scripts.push(element);
        selectedScripts.push(element['scriptName'])
      }
      delete element['Selected']
      allScripts.push(element['scriptName'])
      let scr = allScripts;
      selectedScripts.forEach(element => {
        allScripts = scr
        if (allScripts.includes(element)) {
          let temp1 = allScripts.splice(allScripts.indexOf(element), 1)
          if (allScripts.includes(element)) {
            duplicateStatus = false;
          }
        }
      });
      let nameStatusList = []
      let keywordsStatusList = []
      if (this.scripts.length != 0) {
        this.scripts.forEach(item => {
          if (item['scriptName'].length == 0) {
            nameStatusList.push(false)
          } else if (item['keyword'].length == 0) {
            keywordsStatusList.push(false)
          }
        });
        if (nameStatusList.includes(false)) {
          alert("Script name is empty")
        } else if (keywordsStatusList.includes(false)) {
          alert("keywords are empty")
        } else if (!duplicateStatus) {
          alert("Please remove duplicate script names")
        } else {
          let formData = new FormData();
          formData.append('Scripts', JSON.stringify(temp1));
          formData.append('Operation', 'Mapping')
          console.log('formdata....', formData)
          this.httpClient.post('/api/saveScriptDetails', formData, { responseType: 'text' }).subscribe(data => {
            alert(data)
            this.scriptsLoad()
          }, err => {
          });
        }
      } else {
        alert("Select atleast one")
      }
    })
  }
  save() {
    this.scripts = []
    let flag: boolean;
    let selectedScripts = []
    let allScripts = []
    let duplicateStatus = true;
    this.dataSource.data.forEach(element => {
      if (element.Selected) {
        flag = true;
        delete element['Selected']
        this.scripts.push(element)
      }
    });
    // delete element['Selected']
    if (flag) {
      let formData = new FormData();
      formData.append('Scripts', JSON.stringify(this.scripts));
      formData.append('Operation', 'Mapping')
      this.httpClient.post('/api/saveMappingKeywords', formData, { responseType: 'text' }).subscribe(data => {
        alert(data)
        this.scriptsLoad()
      }, err => {
      });
    } else {
      alert('Select atleast one');
    }
  }
}