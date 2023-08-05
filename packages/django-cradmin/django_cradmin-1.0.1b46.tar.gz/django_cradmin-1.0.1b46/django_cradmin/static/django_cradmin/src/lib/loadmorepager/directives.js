(function() {
  angular.module('djangoCradmin.loadmorepager.directives', []).directive('djangoCradminLoadMorePager', [
    'djangoCradminBgReplaceElement', 'djangoCradminLoadmorepagerCoordinator', function(djangoCradminBgReplaceElement, djangoCradminLoadmorepagerCoordinator) {
      var pagerWrapperCssSelector;
      pagerWrapperCssSelector = '.django-cradmin-loadmorepager';
      return {
        restrict: 'A',
        scope: true,
        controller: function($scope, $element) {
          $scope.loadmorePagerIsLoading = false;
          $scope.getNextPageNumber = function() {
            return $scope.loadmorePagerOptions.nextPageNumber;
          };
          $scope.loadMore = function() {
            var nextPageUrl;
            $scope.loadmorePagerIsLoading = true;
            nextPageUrl = new Url();
            nextPageUrl.query[$scope.loadmorePagerOptions.pageQueryStringAttribute] = $scope.getNextPageNumber();
            return djangoCradminBgReplaceElement.load({
              parameters: {
                method: 'GET',
                url: nextPageUrl.toString()
              },
              remoteElementSelector: $scope.loadmorePagerOptions.targetElementCssSelector,
              targetElement: angular.element($scope.loadmorePagerOptions.targetElementCssSelector),
              $scope: $scope,
              replace: false,
              onHttpError: function(response) {
                return typeof console !== "undefined" && console !== null ? typeof console.error === "function" ? console.error('ERROR loading page', response) : void 0 : void 0;
              },
              onSuccess: function($remoteHtmlDocument) {
                return $element.addClass('django-cradmin-loadmorepager-hidden');
              },
              onFinish: function() {
                return $scope.loadmorePagerIsLoading = false;
              }
            });
          };
        },
        link: function($scope, $element, attributes) {
          var domId;
          $scope.loadmorePagerOptions = {
            pageQueryStringAttribute: "page"
          };
          if ((attributes.djangoCradminLoadMorePager != null) && attributes.djangoCradminLoadMorePager !== '') {
            angular.extend($scope.loadmorePagerOptions, angular.fromJson(attributes.djangoCradminLoadMorePager));
          }
          if ($scope.loadmorePagerOptions.targetElementCssSelector == null) {
            throw Error('Missing required option: targetElementCssSelector');
          }
          domId = $element.attr('id');
          djangoCradminLoadmorepagerCoordinator.registerPager(domId, $scope);
          $scope.$on("$destroy", function() {
            return djangoCradminLoadmorepagerCoordinator.unregisterPager(domId, $scope);
          });
        }
      };
    }
  ]);

}).call(this);
