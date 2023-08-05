#Numpy and sklearn
import numpy as np
#Metric for confusion matrix
from sklearn.metrics import confusion_matrix
#Metric for ROC
from sklearn.metrics import roc_curve, auc
#Metric for Precision-Recall
from sklearn.metrics import precision_recall_curve, average_precision_score
#Matplotlib
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt

import tables as t

from sklearn.preprocessing import label_binarize

#Classification plots

#Confusion matrix
#http://scikit-learn.org/stable/auto_examples/model_selection/plot_confusion_matrix.html
def confusion_matrix_(y_test, y_pred, target_names, normalize=False, title='Confusion matrix', cmap=plt.cm.Blues):
    cm = confusion_matrix(y_test, y_pred)
    if normalize:
        cm = cm.astype('float') / cm.sum(axis=1)[:, np.newaxis]
    np.set_printoptions(precision=2)
    fig = Figure()
    canvas = FigureCanvas(fig)
    ax = fig.add_subplot(111)
    im = ax.imshow(cm, interpolation='nearest', cmap=plt.cm.Blues)
    fig.colorbar(im)
    tick_marks = np.arange(len(target_names))
    ax.set_xticks(tick_marks)
    ax.set_xticklabels(target_names, rotation=45)
    ax.set_yticks(tick_marks)
    ax.set_yticklabels(target_names)
    fig.tight_layout()
    ax.set_title(title)
    ax.set_ylabel('True label')
    ax.set_xlabel('Predicted label')
    return fig

#Receiver operating characteristic (ROC)
#http://scikit-learn.org/stable/auto_examples/model_selection/plot_roc.html
def roc(y_true, y_score, title="ROC curve"):
    '''
        Plot ROC curve based on true labels and model predictions.
        y_score (n_rows * n_classes) - Scores for a given prediction
        y_true  (n_rows * 1) - True label for a given prediction
        Assumes all classes are present in y_true, binarizes and orders.
    '''
    #y_score MUST contain one column per class, so get the number of classes
    #except when is a binary classification
    if len(y_score.shape) == 1:
        n_classes = 2
    else:
        n_classes = y_score.shape[1]

    #Asume y_true is in binary format for now...

    #y_true can be in binarized form or not,
    #if it's not in binary format, binarize
    #binary_format = True
    #if not binary_format:
    
    y_true = label_binarize(y_true, classes=list(set(y_true)))

    #Now that both y_true is in the correct format, check input shape
    #Check y_true and y_score have correct shape

    fpr = dict()
    tpr = dict()
    roc_auc = dict()

    if n_classes>2:
        for i in range(n_classes):
            fpr[i], tpr[i], _ = roc_curve(y_true[:, i], y_score[:, i])
            roc_auc[i] = auc(fpr[i], tpr[i])
        # Compute micro-average ROC curve and ROC area
        fpr["micro"], tpr["micro"], _ = roc_curve(y_true.ravel(), y_score.ravel())
        roc_auc["micro"] = auc(fpr["micro"], tpr["micro"])
    else:
        fpr[1], tpr[1], _ = roc_curve(y_true, y_score)
        roc_auc[1] = auc(fpr[1], tpr[1])
    
    # Plot of a ROC curve for class 1 if binary classifier
    # Plot all classes and micro-average if multiclass classifier
    fig = Figure()
    canvas = FigureCanvas(fig)
    ax = fig.add_subplot(111)
    if n_classes==2:
        ax.plot(fpr[1], tpr[1], label='ROC curve (area = %0.2f)' % roc_auc[1])
    else:
        ax.plot(fpr["micro"], tpr["micro"], label='micro-average ROC curve (area = {0:0.2f})'.format(roc_auc["micro"]))
        for i in range(n_classes):
            ax.plot(fpr[i], tpr[i], label='ROC curve (area = %0.2f)' % roc_auc[i])

    ax.plot([0, 1], [0, 1], 'k--')
    ax.set_xlim([0.0, 1.0])
    ax.set_ylim([0.0, 1.05])
    ax.set_xlabel('False Positive Rate')
    ax.set_ylabel('True Positive Rate')
    ax.set_title('Receiver operating characteristic example')
    ax.legend(loc="lower right")
    return fig

#Receiver operating characteristic (ROC) with cross validation
#http://scikit-learn.org/stable/auto_examples/model_selection/plot_roc.html

#Precision-recall
#http://scikit-learn.org/stable/auto_examples/model_selection/plot_precision_recall.html
def precision_recall(y_true, y_score, title="Precision-Recall curve"):
    '''
        Plot Precision-Recall curve based on true labels and model predictions.
        y_score (n_rows * n_classes) - Scores for a given prediction
        y_true  (n_rows * 1) - True label for a given prediction (assumes binary input)
        Assumes all classes are present in y_true, binarizes and orders.
    '''
    #y_score MUST contain one column per class, so get the number of classes
    #except when is a binary classification
    if len(y_score.shape) == 1:
        n_classes = 2
    else:
        n_classes = y_score.shape[1]

    #Asume y_true is in binary format for now...

    #y_true can be in binarized form or not,
    #if it's not in binary format, binarize
    #binary_format = True
    #if not binary_format:
    
    y_true = label_binarize(y_true, classes=list(set(y_true)))

    #Now that both y_true is in the correct format, check input shape
    #Check y_true and y_score have correct shape
    
    
    precision = dict()
    recall = dict()
    average_precision = dict()

    if n_classes>2:
        for i in range(n_classes):
            precision[i], recall[i], _ = precision_recall_curve(y_true[:, i], y_score[:, i])
            average_precision[i] = average_precision_score(y_true[:, i], y_score[:, i])
        # Compute micro-average ROC curve and ROC area
        precision["micro"], recall["micro"], _ = precision_recall_curve(y_true.ravel(), y_score.ravel())
        average_precision["micro"] = average_precision_score(y_true, y_score, average="micro")
    else:
        precision[1], recall[1], _ = precision_recall_curve(y_true, y_score)
        average_precision[1] = average_precision_score(y_true, y_score)
    
    # Plot of a ROC curve for class 1 if binary classifier
    # Plot all classes and micro-average if multiclass classifier
    fig = Figure()
    canvas = FigureCanvas(fig)
    ax = fig.add_subplot(111)
    if n_classes==2:
        ax.plot(recall[1], precision[1], label='Precision-Recall curve')
    else:
        ax.plot(recall["micro"], precision["micro"], label='micro-average Precision-recall curve (area = {0:0.2f})'.format(average_precision["micro"]))
        for i in range(n_classes):
            ax.plot(recall[i], precision[i], label='P-R curve of class {0} (area = {1:0.2f})'.format(i, average_precision[i]))

    ax.set_xlim([0.0, 1.0])
    ax.set_ylim([0.0, 1.05])
    ax.set_xlabel('Recall')
    ax.set_ylabel('Precision')
    if n_classes==2:
        ax.set_title('Precision-Recall curve: AUC={0:0.2f}'.format(average_precision[1]))
    else:
        ax.set_title(title)
    ax.legend(loc="lower right")
    return fig

#http://scikit-learn.org/stable/auto_examples/ensemble/plot_forest_importances.html
def feature_importance(model, feature_list=None, n=None):
    #If no feature_list is provided, assign numbers
    total_features = len(model.feature_importances_)
    feature_list = range(total_features) if feature_list is None else feature_list
    #Plot all features if n is not provided, otherwise plot top n features
    n = len(feature_list) if n is None else n

    f_imp = t._compute_feature_importances(model, feature_list)
    importances = map(lambda x:x['importance'], f_imp)[:n]
    stds = map(lambda x:x['std'], f_imp)[:n]
    names = map(lambda x:x['name'], f_imp)[:n]

    fig = Figure()
    canvas = FigureCanvas(fig)
    ax = fig.add_subplot(111)
    ax.set_title("Feature importances")
    ax.bar(range(len(importances)), importances, color="r", yerr=stds, align="center")
    ax.set_xticks(range(len(names)))
    ax.set_xticklabels(names, rotation=90)
    ax.set_xlim([-1, 10])
    return fig


#clustering plots

#