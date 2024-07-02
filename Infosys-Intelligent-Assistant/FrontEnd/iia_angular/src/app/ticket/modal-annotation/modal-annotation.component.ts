/* Copyright 2022 Infosys Ltd.Use of this source code is governed by MIT license that can be found in the LICENSE file or athttps://opensource.org/licenses/MIT.*/
import { Component, Input, OnInit } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { NgbActiveModal } from '@ng-bootstrap/ng-bootstrap';
@Component({
    selector: 'modal-annotation',
    templateUrl: './modal-annotation.component.html',
    styleUrls: ['./modal-annotation.component.css']
})
export class AnnotationModalComponent implements OnInit {
    @Input() ticketNumber: string;
    customerID: number = 1;
    datasetID: number = 1;
    tagsLst: any = [];
    wordDocLst: any = [];
    saveState: boolean;
    showMsg: boolean;
    msg: string;
    tagShowMsg: boolean;
    tagSaveState: boolean;
    newTagState: boolean;
    deleteTagState: boolean;
    tagName: string;
    tagNameDoc: any = {};
    checkedLst: any = {};
    tagDeleteState: boolean;
    constructor(private httpClient: HttpClient, public activeModal: NgbActiveModal) { }
    private arraycolor: any = ["#F0F8FF", "#E0FFFF", "#F0FFF0", "#FFF0F5", "#FFF8DC", "#E6E6FA", "#FFE4E1", "#AFEEEE", "#DCDCDC", "#EEE8AA",
        "#FFC0CB", "#ADD8E6", "#D8BFD8", "#DDA0DD", "#40E0D0", "#FFA07A", "#FFF5EE", "#87CEEB", "#DEB887", "#66CDAA", "#F08080", "#5F9EA0"];
    ngOnInit() {
        this.httpClient.get('/api/get_entity_tags/' + this.ticketNumber).subscribe(data => {
            this.tagsLst = data;
            console.log(this.tagsLst)
            this.tagsLst.splice(this.tagsLst.indexOf('O'), 1);
            console.log(this.tagsLst);
            let index = 0;
            this.tagsLst.forEach(tagName => {
                this.tagNameDoc[tagName] = this.arraycolor[Math.floor(Math.random() * this.arraycolor.length)];
                console.log(this.tagNameDoc[tagName])
                this.checkedLst[tagName] = false;
                index++;
            });
        }, err => {
            console.error('Could not get tags, error : ' + err);
        });
        this.httpClient.get('/api/incident_entity/' + this.customerID + '/' + this.ticketNumber).subscribe(data => {
            this.wordDocLst = data;
            this.wordDocLst.forEach(wordDoc => {
                for (let key in wordDoc)
                    if (this.tagNameDoc[wordDoc[key]] == undefined && wordDoc[key] != 'O') {
                        this.tagNameDoc[wordDoc[key]] = this.arraycolor[Math.floor(Math.random() * this.arraycolor.length)];
                        this.checkedLst[wordDoc[key]] = false;
                    }
            });
        }, err => {
            console.log('Could not get description, error : ' + err);
        });
    }
    addclassifier(classClr: string) {
        let word: string;
        var selectedText = window.getSelection().toString();
        selectedText = selectedText.trim();
        alert(selectedText)
        if (selectedText != '') {
            let index = 0;
            let chosenIndex = -1;
            this.wordDocLst.forEach(wordDoc => {
                if (wordDoc[selectedText] != undefined) {
                    chosenIndex = index;
                    wordDoc[selectedText] = classClr;
                    index++;
                } else
                    index++;
            });
            if (chosenIndex < 0) {
                let fullWord: string = ''; let key: string;
                let selectedTextLst: string[] = [];
                let lengthOfSelWrds: number;
                for (let word of selectedText.split(' ')) { selectedTextLst.push(word.trim()); }
                lengthOfSelWrds = selectedTextLst.length;
                if (lengthOfSelWrds > 1) {
                    index = 0; let i: number;
                    let word = selectedTextLst[0];
                    let tempWordDocLst = this.wordDocLst;
                    this.wordDocLst.forEach(function (wordDoc, index) {
                        if (wordDoc[word] != undefined) {
                            for (i = 1; i < lengthOfSelWrds; i++)
                                if (!(selectedTextLst[i] in tempWordDocLst[index + i]))
                                    break;
                            if (i == lengthOfSelWrds)
                                for (i = 0; i < lengthOfSelWrds; i++)
                                    tempWordDocLst[index + i][selectedTextLst[i]] = classClr;
                        }
                    });
                }
            }
        }
    }
    saveEntityTags() {
        this.saveState = false;
        this.httpClient.put('/api/annotated_data/' + this.ticketNumber, this.wordDocLst, { 'responseType': 'text' })
            .subscribe(msg => {
                if (msg == 'success') {
                    this.msg = 'Saved Successfully!';
                    this.saveState = true;
                } else {
                    this.msg = 'Could not Save! Please try again';
                }
            }, err => {
                this.msg = 'Could not Save! Please try again later';
                console.error('Could not save! error : ' + err);
            });
        this.showMsg = true;
    }
    removeColor(key: string, index: number) {
        this.wordDocLst[index][key] = 'O';
        index = 0;
        this.wordDocLst.forEach(wordDoc => {
            if (wordDoc[key] != undefined) {
                this.wordDocLst[index][key] = 'O';
                index++;
            } else
                index++;
        });
    }
    disableMsg() {
        this.showMsg = false;
    }
    newTag() {
        this.newTagState = true;
    }
    deleteTagBtnClick() {
        this.deleteTagState = true;
    }
    deleteTag() {
        this.deleteTagState = true;
        this.tagDeleteState = false;
        let tagsToDelete: string[] = [];
        for (let key in this.checkedLst)
            if (this.checkedLst[key]) {
                tagsToDelete.push(key);
            }
        if (tagsToDelete.length > 0) {
            this.httpClient.post('/api/remove_tag_name/' + this.customerID + '/' + this.datasetID + '/' + this.ticketNumber, tagsToDelete)
                .subscribe(data => {
                    this.tagNameDoc = {};
                    this.wordDocLst = data;
                    this.wordDocLst.forEach(wordDoc => {
                        for (let key in wordDoc)
                            if (this.tagNameDoc[wordDoc[key]] == undefined && wordDoc[key] != 'O') {
                                this.tagNameDoc[wordDoc[key]] = this.arraycolor[Math.floor(Math.random() * this.arraycolor.length)];
                                this.checkedLst[wordDoc[key]] = false;
                            }
                    });
                }, err => {
                    this.msg = 'Could not remove! Please try agin later';
                    console.error('Could not remove! error : ' + err);
                });
        } else {
            this.msg = 'Tag Name should be selected!';
        }
        this.tagShowMsg = true;
    }
    saveNewTag() {
        this.tagSaveState = false;
        if (this.tagName != '' && this.tagName != undefined) {
            this.httpClient.put('/api/save_tag_name/' + this.customerID + '/' + this.datasetID + '/' + this.tagName, null, { 'responseType': 'text' })
                .subscribe(msg => {
                    if (msg == 'success') {
                        this.tagNameDoc[this.tagName] = this.arraycolor[Math.floor(Math.random() * this.arraycolor.length)];
                        this.msg = 'Saved Successfully!';
                        this.tagSaveState = true;
                        this.tagName = '';
                        console.log('saved successfully!');
                    }
                    else {
                        this.msg = 'Could not Save! Please try again';
                        console.warn('Could not save! Please try again');
                    }
                }, err => {
                    this.msg = 'Could not save! Please try agin later';
                    console.error('Could not save! error : ' + err);
                });
        } else {
            this.msg = 'Tag Name should not be empty!';
        }
        this.tagShowMsg = true;
    }
    cancel() {
        this.newTagState = false;
        this.tagShowMsg = false;
        this.deleteTagState = false;
        for (let key in this.checkedLst)
            this.checkedLst[key] = false;
    }
}