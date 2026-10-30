from common import Bank
from r3_acids import add_acids
from r3_redox import add_redox
from r3_radicals import add_radicals
from r3_pairs import add_pairs

b=Bank('R3','reactivity-3',{'R3.1':'Proton transfer reactions','R3.2':'Electron transfer reactions','R3.3':'Electron sharing reactions','R3.4':'Electron-pair sharing reactions'})
add_acids(b)
add_redox(b)
add_radicals(b)
add_pairs(b)
for question in b.questions:
    if question['questionType']=='data-based':
        question['stem']='The following data are constructed for this question. '+question['stem']
    if question['id'] in ('ib-chem-r3-028','ib-chem-r3-030'):
        question['stem']+=' Assume the buffer approximation remains valid.'
    if question['id']=='ib-chem-r3-052':
        question['parts'][0]['prompt']=r'Calculate the standard Gibbs energy change in $\mathrm{kJ\,mol^{-1}}$.'
b.write(120)
