angular.module('proso.goals').run(['$templateCache', function($templateCache) {
  'use strict';

  $templateCache.put('static/tpl/goal-progress_tpl.html',
    "<div class=\"goal-progress\" ng-if=\"goal\"><span class=\"pull-left start-date\">{{goal.start_date | date}}</span> <span class=\"pull-right finish-date\">{{goal.finish_date | date}}</span><div class=\"progress\" tooltip-placement=\"bottom\" tooltip=\"{{'Postup plnění cíle' | trans }}\"><span style=\"width: {{goal.progress * 100}}%\" tooltip=\"{{'Splněno' | trans }}\" ng-style=\"{{goal|stripedStyle:true}}\" class=\"progress-bar progress-bar-learned\"></span> <span style=\"width: {{goal.progress_diff * 100}}%\" ng-show=\"goal.needs_practice && !goal.behind_schedule\" tooltip=\"{{'Dnešní nesplněné procvičování' | trans }}\" class=\"progress-bar progress-bar-warning\"></span> <span style=\"width: {{goal.progress_diff * 100}}%\" ng-show=\"goal.behind_schedule\" tooltip=\"{{'Více než den nesplněného procvičování' | trans }}\" ng-style=\"{{goal|stripedStyle}}\" class=\"progress-bar progress-bar-unlearned\"></span></div></div>"
  );


  $templateCache.put('static/tpl/personal-goals-page_tpl.html',
    "<div class=\"overview\" ng-init=\"editRights=true\"><div class=\"col-sm-offset-2 col-sm-8\"><div personal-goals=\"\"></div></div></div>"
  );


  $templateCache.put('static/tpl/personal-goals_tpl.html',
    "<h2>{{'Osobní cíle' | trans }} <i class=\"glyphicon glyphicon-question-sign\" popover-title=\"{{'Chceš se naučit některou mapu do určitého data?'| trans}}\" popover=\"{{'Nastav si cíl a systém ti podle tvých aktuálních znalostí rozloží procvičování na jednotlivé dny.' | trans }}\" popover-append-to-body=\"true\" popover-placement=\"bottom\" popover-trigger=\"mouseenter\"></i> <i ng-click=\"addGoal()\" ng-show=\"editRights\" tooltip=\"{{'Vytvořit cíl' | trans }}\" class=\"pull-right glyphicon glyphicon-plus-sign\"></i></h2><div ng-hide=\"loaded\" class=\"loading-indicator\"></div><div class=\"alert alert-info\" ng-show=\"goals.length === 0\">{{'Žádné cíle zatím nebyly stanoveny' | trans }}</div><ul><li ng-repeat=\"goal in goals\" class=\"goal striped-row\"><span class=\"btn-group pull-right\" ng-show=\"editRights\"><a href=\"#/practice/{{goal.map.code}}/{{goal.type.slug}}\" tooltip=\"{{'Dnes již není třeba procvičovat' | trans}}\" tooltip-trigger=\"{{ goal.needs_practice ? 'none' : 'mouseenter'}}\" tooltip-append-to-body=\"true\" class=\"btn btn-primary\"><i class=\"glyphicon glyphicon-check\"></i> {{'Procvičovat'| trans}}</a> <a ng-click=\"deleteGoal(goal)\" tooltip=\"{{'Odstranit cíl' | trans}}\" tooltip-append-to-body=\"true\" class=\"btn btn-default\"><i ng-hide=\"goal.deleting\" class=\"glyphicon glyphicon-trash\"></i> <i ng-show=\"goal.deleting\" class=\"icon-loading\"></i></a></span><h3>{{goal.map.name}} - {{goal.type.name}}</h3><div class=\"clearfix\"></div><div goal-progress=\"\"></div></li></ul>"
  );

}]);
