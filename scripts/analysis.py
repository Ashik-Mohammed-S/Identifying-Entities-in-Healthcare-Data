from scripts.analysis_common import *
from scripts.fetch_data import ensure_data

def sentences(path):
    groups=[];current=[]
    for line in path.read_text(encoding='utf-8').splitlines():
        if line.strip():current.append(line.strip())
        elif current:groups.append(current);current=[]
    if current:groups.append(current)
    return groups

def spans(labels):
    out=set();start=0
    while start<len(labels):
        label=labels[start];end=start+1
        while end<len(labels) and labels[end]==label:end+=1
        if label!='O':out.add((start,end,label))
        start=end
    return out

def run(mode='full'):
    import spacy,sklearn_crfsuite
    from spacy.tokens import Doc
    from sklearn.metrics import classification_report,f1_score
    data=ensure_data(ROOT/'dataset')
    train=sentences(data/'train_sent');y_train=sentences(data/'train_label')
    test=sentences(data/'test_sent');y_test=sentences(data/'test_label')
    assert len(train)==len(y_train) and len(test)==len(y_test)
    assert all(len(x)==len(y) for x,y in zip(train+test,y_train+y_test))
    if mode=='quick':train,y_train=train[:400],y_train[:400]
    nlp=spacy.load('en_core_web_sm',disable=['parser','ner'])
    def features(rows):
        all_features=[]
        docs=(Doc(nlp.vocab,words=words) for words in rows)
        for words,doc in zip(rows,nlp.pipe(docs,batch_size=64)):
            seq=[]
            for i,word in enumerate(words):
                item={'bias':1.,'word':word.lower(),'suffix2':word[-2:],'suffix3':word[-3:],'upper':word.isupper(),
                    'title':word.istitle(),'digit':word.isdigit(),'pos':doc[i].pos_,'begin':i==0,'end':i==len(words)-1}
                if i:item.update(previous=words[i-1].lower(),previous_pos=doc[i-1].pos_)
                if i+1<len(words):item.update(next=words[i+1].lower(),next_pos=doc[i+1].pos_)
                seq.append(item)
            all_features.append(seq)
        return all_features
    X_train=features(train);X_test=features(test)
    model=sklearn_crfsuite.CRF(algorithm='lbfgs',c1=.1,c2=.1,max_iterations=100,all_possible_transitions=True)
    model.fit(X_train,y_train);pred=model.predict(X_test)
    gold=[v for row in y_test for v in row];estimated=[v for row in pred for v in row]
    tp=fp=fn=0
    for actual,guessed in zip(y_test,pred):
        a,b=spans(actual),spans(guessed);tp+=len(a&b);fp+=len(b-a);fn+=len(a-b)
    precision=tp/(tp+fp) if tp+fp else 0;recall=tp/(tp+fn) if tp+fn else 0
    labels=sorted(set(gold)-{'O'})
    report={'objective':'Identify disease and treatment spans in supplied tokenized healthcare sentences.',
        'analysis_type':'supervised sequence labeling','target':'D / T / O token labels and contiguous disease/treatment spans',
        'train_sentences':len(train),'test_sentences':len(test),'train_tokens':sum(map(len,train)),'test_tokens':len(gold),
        'split':'Original provided training/test corpora. Exact token/label alignment verified; no test labels used for fitting.',
        'metrics':{'entity_token_micro_f1':f1_score(gold,estimated,labels=labels,average='micro',zero_division=0),
            'exact_span_precision':precision,'exact_span_recall':recall,'exact_span_f1':2*precision*recall/(precision+recall) if precision+recall else 0},
        'class_report':classification_report(gold,estimated,labels=labels,output_dict=True,zero_division=0),
        'interpretation':'O-token accuracy alone is not the objective. Span metrics require matching label, start and end. This is dataset annotation research, not clinical decision support.'}
    summary=pd.DataFrame({'label':labels,'gold_tokens':[gold.count(c) for c in labels],'predicted_tokens':[estimated.count(c) for c in labels]})
    return finish(report,summary)
