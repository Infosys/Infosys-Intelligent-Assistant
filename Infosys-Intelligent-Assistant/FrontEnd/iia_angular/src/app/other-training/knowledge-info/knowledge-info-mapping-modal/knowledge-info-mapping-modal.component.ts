/* Copyright 2022 Infosys Ltd.Use of this source code is governed by MIT license that can be found in the LICENSE file or athttps://opensource.org/licenses/MIT.*/
import { Component, OnInit, Inject, ViewChild, ElementRef } from '@angular/core';
import { MAT_DIALOG_DATA, MatDialogRef } from '@angular/material/dialog';
import { HttpClient } from '@angular/common/http';


@Component({
  selector: 'app-knowledge-info-mapping-modal',
  templateUrl: './knowledge-info-mapping-modal.component.html',
  styleUrls: ['./knowledge-info-mapping-modal.component.css']
})

export class KnowledgeInfoMappingModalComponent implements OnInit {


  @ViewChild('newColumn') newColumnInput: ElementRef;
  accountColumnsLst: string[];
  iiaColumnsLst: string[];
  selectedIIAColumn: string;
  selectedAccColumn: string;
  dataSource;
  newIIAColumnState: boolean;
  newIIAColumnName: string;


  constructor (@Inject(MAT_DIALOG_DATA) public data: any, private httpClient: HttpClient, 
  private matDialogRef: MatDialogRef<KnowledgeInfoMappingModalComponent>) {}

  ngOnInit () {
    this.accountColumnsLst = this.data['accountColumnsLst'];
    this.iiaColumnsLst = this.data['iiaColumnsLst'];
    this.dataSource = [];
    // this.dataSource = this.data['mapedDataLst'];
    this.iiaColumnsLst.push('Create NER Tag..');
  }

  mapColumns () {
    if (this.newIIAColumnName != undefined && this.newIIAColumnName != '') {
      this.iiaColumnsLst.splice(-1, 0, this.newIIAColumnName);
      this.selectedIIAColumn = this.newIIAColumnName;
      this.newIIAColumnState = false;
      this.newIIAColumnName = '';
    }

    if (this.selectedIIAColumn != '' && this.selectedAccColumn != '') {
      this.dataSource.push({ account_column: this.selectedAccColumn, iia_column: this.selectedIIAColumn});
      this.accountColumnsLst.splice(this.accountColumnsLst.indexOf(this.selectedAccColumn), 1);
      this.iiaColumnsLst.splice(this.iiaColumnsLst.indexOf(this.selectedIIAColumn), 1);
      this.selectedAccColumn = '';
      this.selectedIIAColumn = '';
    }
  }

  deleteMapedInfo (index: number) {
    this.accountColumnsLst.push(this.dataSource[index].account_column);
    this.iiaColumnsLst.splice(-1, 0, this.dataSource[index].iia_column);
    this.dataSource.splice(index, 1);
  }

  saveMapedInfo () {
    const formData = new FormData();
    formData.append('mappedHeaders', JSON.stringify(this.dataSource));
    formData.append('knowledgeInfoDetails', this.data['file']);
    this.httpClient.post('/api/ner/saveKnowledgeInfo', formData, {responseType: 'text'}).subscribe(response => {
      // alert(response);
      this.matDialogRef.close();
    }, err => {
      console.error(err);      
    });
  }

  IIAColumnChange () {
    if (this.selectedIIAColumn == 'Create NER Tag..') {
      this.newIIAColumnState = true;
      this.selectedIIAColumn = '';
      setTimeout(()=>{
        this.newColumnInput.nativeElement.focus();
      }, 0);
    }
  }

  disableNewIIANameState () {
    this.selectedIIAColumn = '';
    this.newIIAColumnState = false;
    this.newIIAColumnName = '';
  }

}
