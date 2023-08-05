(function() {
  angular.module('djangoCradmin.multiselect2.services', []).factory('djangoCradminMultiselect2Coordinator', function() {
    /*
    Coordinates between djangoCradminMultiselect2Select
    and djangoCradminMultiselect2Target.
    */

    var Coordinator;
    Coordinator = (function() {
      function Coordinator() {
        this.targets = {};
      }

      Coordinator.prototype.registerTarget = function(targetDomId, targetScope) {
        return this.targets[targetDomId] = targetScope;
      };

      Coordinator.prototype.unregisterTarget = function(targetDomId, targetScope) {
        return del(this.targets[targetDomId]);
      };

      Coordinator.prototype.__getTargetScope = function(targetDomId) {
        var targetScope;
        targetScope = this.targets[targetDomId];
        if (targetScope == null) {
          throw Error("No target with ID '" + targetDomId + "' registered with djangoCradminMultiselect2Coordinator.");
        }
        return targetScope;
      };

      Coordinator.prototype.targetScopeExists = function(targetDomId) {
        return this.targets[targetDomId] != null;
      };

      Coordinator.prototype.select = function(selectScope) {
        var targetScope;
        targetScope = this.__getTargetScope(selectScope.getTargetDomId());
        return targetScope.select(selectScope);
      };

      Coordinator.prototype.onDeselect = function(selectButtonDomId) {
        var $selectElement, selectScope, targetScope;
        $selectElement = angular.element('#' + selectButtonDomId);
        if ($selectElement != null) {
          selectScope = $selectElement.isolateScope();
          selectScope.onDeselect();
          targetScope = this.__getTargetScope(selectScope.getTargetDomId());
          return targetScope.onDeselect(selectScope);
        } else {
          return console.log("Element #" + selectButtonDomId + " is not in the DOM");
        }
      };

      Coordinator.prototype.isSelected = function(targetDomId, selectScope) {
        var targetScope;
        targetScope = this.__getTargetScope(targetDomId);
        return targetScope.isSelected(selectScope);
      };

      return Coordinator;

    })();
    return new Coordinator();
  });

}).call(this);
