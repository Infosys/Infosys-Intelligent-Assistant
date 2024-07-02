/* Copyright 2022 Infosys Ltd.Use of this source code is governed by MIT license that can be found in the LICENSE file or athttps://opensource.org/licenses/MIT.*/
import { Routes,RouterModule } from '@angular/router';
import { DashboardComponent } from '../../dashboard/dashboard.component';
import { TrainingComponent }   from '../../training/training.component';
import { AlgorithmFilterComponent }   from '../../training/algorithm-filter/algorithm-filter.component';
import { AlgorithmInformationComponent }   from '../../training/algorithm-information/algorithm-information.component';
import { UserPreferenceComponent } from '../../user-preference/user-preference.component';
import { ResourcePlanningComponent } from '../../resource-planning/resource-planning.component';
import { ResourceDetailsComponent } from '../../resource-planning/resource-details/resource-details.component';
import { ApplicationDetailsComponent } from '../../resource-planning/application-details/application-details.component';
import { RoasterDetailsComponent } from '../../resource-planning/roaster-details/roaster-details.component';
import { ShiftDetailsComponent } from '../../resource-planning/roaster-details/shift-details/shift-details.component';
import { TicketWeightageComponent } from '../../resource-planning/ticket-weightage/ticket-weightage.component'
import { PredictComponent } from '../../predict/predict.component';
import { TicketComponent } from '../../ticket/ticket.component';
import { RetrainingComponent } from '../../retraining/retraining.component';
import { ApplicaitonLevelSettingsComponent } from '../../admin/application-level-settings/application-level-settings.component';
import { ITSMDetialsComponent } from '../../admin/itsm-details/itsm-details.component';
import { NotificationsComponent } from '../../admin/notifications/notifications.component';
import { OtherSettingsComponent } from '../../admin/other-settings/other-settings.component';
import { TeamDetailsComponent } from '../../admin/team-details/team-details.component';
import { AdminComponent } from '../../admin/admin.component'
import { componentNeedsResolution } from '@angular/core/src/metadata/resource_loading';
import {AboutPageComponent } from '../../about-page/about-page.component';
import {AddUserComponent} from '../../admin/add-user/add-user.component';
import {ScriptsConfigurationComponent} from '../../admin/scripts-configuration/scripts-configuration.component';
import {AdminUserManageComponent} from '../../admin/admin-user-manage/admin-user-manage.component';
import {TagsTrainingComponent} from '../../admin/tags-training/tags-training.component'
import {TagSettingsComponent} from '../../admin/tag-settings/tag-settings.component';
import {OtherTrainingComponent} from '../../other-training/other-training.component';
import {BOTimageAnalysisComponent} from '../../other-training/BOT-imageanalysis/BOT-imageanalysis.component';
import { PMAComponent } from '../../training/PMA/PMA.component';
export const AdminLayoutRoutes: Routes = [
    { path: 'workbench', component: DashboardComponent },    
    { path: 'training', component: TrainingComponent},
    { path: 'algorithminformation/:datasetID', component: AlgorithmInformationComponent },
    { path: 'algorithmfilter/:datasetID',component: AlgorithmFilterComponent},
    { path: 'predict', component: PredictComponent},
    { path: 'tickets/:datasetID', component: TicketComponent},
    {
        path: 'assignment',
        component: ResourcePlanningComponent
    },
    { path: 'resourceplanning', component: ResourcePlanningComponent},
    { path: 'resourceDetails/:teamName', component: ResourcePlanningComponent},
    { path: 'roasterDetails/:teamName', component: RoasterDetailsComponent},
    { path: 'ticketWeightage', component: ResourcePlanningComponent},
    { path: 'shiftdetails/:customerId/:chosenTeam/:emailId/:resourceName', component: ShiftDetailsComponent},
    { path: 'retraining', component: RetrainingComponent},
    { path: 'retraining', component: RetrainingComponent},
    { path: 'applicationLevelSettings', component: ApplicaitonLevelSettingsComponent},
    { path: 'itsmDetails', component: ITSMDetialsComponent},
    { path: 'notifications', component: NotificationsComponent},
    { path: 'otherSettings', component: OtherSettingsComponent},
    { path: 'teamDetails', component: TeamDetailsComponent},
    { path: 'admin' , component: AdminComponent},
    { path: 'about' , component: AboutPageComponent},
    { path: 'userManage' , component: AdminUserManageComponent},
    { path: 'scripts' , component: ScriptsConfigurationComponent},
    { path: 'tags' , component: TagsTrainingComponent},
    { path: 'tagSettings' , component: TagSettingsComponent},
    { path: 'otherTraining' , component : OtherTrainingComponent},
    { path: 'screenShotAnalysis' , component : BOTimageAnalysisComponent},
    { path: 'PMA',component :  PMAComponent},
];
