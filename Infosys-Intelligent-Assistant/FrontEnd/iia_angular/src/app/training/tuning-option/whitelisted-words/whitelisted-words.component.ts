/* Copyright 2022 Infosys Ltd.Use of this source code is governed by MIT license that can be found in the LICENSE file or athttps://opensource.org/licenses/MIT.*/
import { Component, Input, OnInit } from '@angular/core';
import { NgbModal, NgbActiveModal, ModalDismissReasons } from '@ng-bootstrap/ng-bootstrap';
import { HttpClient } from '@angular/common/http';
import { ViewEncapsulation } from '@angular/core';
@Component({
  selector: 'app-whitelisted-words',
  templateUrl: './whitelisted-words.component.html',
  styleUrls: ['./whitelisted-words.component.css'],
  encapsulation: ViewEncapsulation.None
})
export class WhitelistedWordsComponent implements OnInit {
  @Input() dataToTakeAsInput: any;
  closeResult: string;
  incidentTicketsData: any = [];
  private customerId: number = 1;
  private retrieveCount: number;
  private retrieveKeywords: any = [];
  public whiteListwordDetails: any = [];
  private AddListwordDetails: any = [];
  private data3: any = [];
  private newAttribute: any = {};
  constructor(private httpClient: HttpClient, private modalService: NgbModal, public activeModal: NgbActiveModal) {
  }
  ngOnInit() {
    this.incidentTicketsData = [];
    this.dataToTakeAsInput['PredictedValues'].forEach(ticket => {
      this.incidentTicketsData.push(ticket);
    });
    this.httpClient.get('/api/getWhiteListWords/' + this.customerId + "/" + this.dataToTakeAsInput['DatasetID'] + "/" + this.dataToTakeAsInput['PredictedField'])
      .subscribe(data => {
        if (data) {
          data[0]["WhiteListed_Words"].forEach((selection) => {
            this.retrieveKeywords.push(selection);
          });
          this.retrieveCount = 0;
          for (let i = 0; i < this.retrieveKeywords.length; i++) {
            for (let j = 0; j < this.retrieveKeywords[i]['Value'].length; j++) {
              this.whiteListwordDetails.push({
                Field_Name: this.retrieveKeywords[i]['Field_Name'],
                pred_fields: this.incidentTicketsData, Value: this.retrieveKeywords[i]['Value'][j]['word'],
                Weightage: this.retrieveKeywords[i]['Value'][j]['weightage']
              });
            }
          }
          this.retrieveCount = this.whiteListwordDetails.length;
        }
      },
        err => {
          console.log(err);
          throw "";
        });
  }
  editField: string;
  updateList(id: number, property: string, event: any) {
    const editField = event.target.textContent;
    this.whiteListwordDetails[id][property] = editField;
  }
  remove(id: any) {
    if (this.whiteListwordDetails.length == this.retrieveCount) {
      this.httpClient.delete('/api/deleteWhiteListWords/' + this.customerId + '/' + this.dataToTakeAsInput['DatasetID'] + '/' + this.dataToTakeAsInput['PredictedField'] + '/' + this.whiteListwordDetails[id]['Field_Name'] + '/' + this.whiteListwordDetails[id]['Value'], { responseType: 'text' }).subscribe(data => {
        if (data == 'success') {
          this.whiteListwordDetails.splice(id, 1);
          this.retrieveCount = (this.retrieveCount - 1);
        }
      });
    }
    else
      this.whiteListwordDetails.splice(id, 1);
  }
  add() {
    this.newAttribute = {
      Field_Name: '',
      pred_fields: this.incidentTicketsData, Value: '', Weightage: 0
    };
    this.whiteListwordDetails.push(this.newAttribute)
    this.AddListwordDetails.push(this.newAttribute)
    //}
  }
  changeValue(id: number, property: string, event: any) {
    this.editField = event.target.textContent;
  }
  save() {
    var seen = {};
    let status = 0;
    let resultToReturn = false;
    for (let i = 0; i < this.whiteListwordDetails.length; i++) { // nested for loop
      for (let j = 0; j < this.whiteListwordDetails.length; j++) {
        // prevents the element from comparing with itself
        if (i !== j) {
          // check if elements' values are equal
          if (this.whiteListwordDetails[i]['Field_Name'] === this.whiteListwordDetails[j]['Field_Name'] && this.whiteListwordDetails[i]['Value'] === this.whiteListwordDetails[j]['Value']) {
            // duplicate element present                                
            resultToReturn = true;
            break;
          }
        }
      }
      if (resultToReturn) {
        break;
      }
    }
    var hasDuplicates = this.whiteListwordDetails.some(function (currentObject) {
      if (currentObject.Value != "" && currentObject.Field_Name != "") {
        if (seen.hasOwnProperty(currentObject.Field_Name) && seen.hasOwnProperty(currentObject.Value)) {
          return true;
        }
      } // Current name is being seen for the first time
      if (currentObject.Field_Name == "" || currentObject.Value == "" || currentObject.Weightage == "") {
        status = 1;
      }
      if (currentObject.Weightage > 1 || currentObject.Weightage < 0 || currentObject.Weightage == undefined) {
        status = 2;
      }
      if (currentObject.Value.trim() == '') {
        status = 3;
      }
      return (seen[currentObject.Value] = false, seen[currentObject.Field_Name] = false, seen[currentObject.Weightage] = false);
    });
    if (resultToReturn) {
      alert("Duplicate Keywords aren't allowed");
    }
    if (status == 1) {
      alert("Empty rows aren't allowed");
    }
    if (status == 2) {
      alert("Weightage value should be in between 0-1")
    }
    if (status == 3) {
      alert("Spaces not allowed")
    }
    if (!resultToReturn && status == 0) {
      let data2 = {};
      this.data3 = [];
      for (let i = 0; i < this.whiteListwordDetails.length; i++) {
        this.data3.push({ 'field_name': this.whiteListwordDetails[i]['Field_Name'], 'keyword': this.whiteListwordDetails[i]['Value'].trim(), 'weighatge': this.whiteListwordDetails[i]['Weightage'] });
      }
      data2['words'] = this.data3;
      this.httpClient.post('/api/updateWhiteListWords/' + this.customerId + '/' + this.dataToTakeAsInput['DatasetID'] + '/' + this.dataToTakeAsInput['PredictedField'], data2, { responseType: 'text' }).subscribe(data => {
        this.retrieveCount = this.whiteListwordDetails.length;
      });
      alert("Saved Successfully")
    }
  }
  open(content) {
    this.modalService.open(content, { ariaLabelledBy: 'modal-basic-title', size: "lg" }).result.then((result) => {
      this.closeResult = 'Closed with: ${result}';
    });
  }
}
