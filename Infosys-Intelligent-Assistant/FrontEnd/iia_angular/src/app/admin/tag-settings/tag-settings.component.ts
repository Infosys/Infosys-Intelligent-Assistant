/* Copyright 2022 Infosys Ltd.Use of this source code is governed by MIT license that can be found in the LICENSE file or athttps://opensource.org/licenses/MIT.*/
import { Component, OnInit } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { logging } from 'selenium-webdriver';
@Component({
    selector: 'app-tag-settings',
    templateUrl: './tag-settings.component.html',
    styleUrls: ['./tag-settings.component.css']
})
export class TagSettingsComponent implements OnInit {
    selected = {};
    uniqueFieldSettings = {};
    clusterDocLst: any = [];
    chosenCluster: any = {};
    tmpClstrNme: string;
    customerId: number = 1;
    datasetId: number = 1;
    clstrNmeEditState: boolean = false;
    clusterId: number;
    clstrChoosedState: boolean = false;
    editedDocIndex: any = [];
    loading: boolean = false;
    constructor(private httpClient: HttpClient) { }
    ngOnInit() {
        this.httpClient.get('/api/loadCluster').subscribe(data => {
            if (data != []) {
                let index = 0;
                this.clusterDocLst = data;
                this.clusterDocLst.forEach(clusterDoc => {
                    clusterDoc['index'] = index;
                    index++;
                });
            } else
                console.warn('Could not load cluster details! Empty response from api');
        }, err => {
            console.error('Could not load cluster details : ' + err);
        });
    }
    clusterChange() {
        this.clusterId = this.chosenCluster['index'];
        this.clstrChoosedState = true;
    }
    editClstrNme() {
        this.tmpClstrNme = this.chosenCluster.clusterName;
        this.clstrNmeEditState = true;
    }
    cancelEditClstrNme() {
        this.tmpClstrNme = '';
        this.clstrNmeEditState = false;
    }
    saveNewClutserName() {
        this.clusterDocLst[this.clusterId].clusterName = this.tmpClstrNme;
        this.clstrNmeEditState = false;
    }
    focusOutFromTagInput() {
        if (this.editedDocIndex.indexOf(this.clusterId) < 0)
            this.editedDocIndex.push(this.clusterId);
    }
    SaveClstrDetails() {
        if (this.editedDocIndex != [])
            this.editedDocIndex.forEach(index => {
                this.clusterDocLst[index]['values'].forEach(value => {
                    if (typeof (value) == 'object') {
                        this.clusterDocLst[index]['values'].splice(this.clusterDocLst[index]['values'].indexOf(value), 1, value['value']);
                    }
                });
            });
        this.clusterDocLst.forEach(clstrDoc => {
            delete clstrDoc['index'];
        });
        this.httpClient.post('/api/saveClusterDetails/' + this.customerId + '/' + this.datasetId, this.clusterDocLst, { 'responseType': 'text' })
            .subscribe(msg => {
                if (msg == 'success')
                    console.log('Saved successfully!');
                else
                    console.warn('Could not save details! failure response from backend');
            }, err => {
                console.error(err);
            });
    }
}