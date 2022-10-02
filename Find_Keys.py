#!/usr/bin/env python
# coding: utf-8

# In[17]:


import numpy as np
from pyfinite import ffield
import pickle


# In[18]:


F = ffield.FField(7, gen=0x83, useLUT=-1)


# In[19]:


field_128 = ffield.FField(7, gen=0x83, useLUT=-1)


# In[20]:


expo = []
rang  =128
for i in range(rang):
    expo.append([-1]*128)

def Mul(op1,op2):
    return field_128.Multiply(op1,op2)

def Exponent(e, power):
    if(expo[e][power]!=-1):
      return expo[e][power]
    
    if(power==0):
          return 1
    elif(power == 1):
        return e
    else:
        expo[e][power] = Mul(e,Exponent(e,power-1))
        return expo[e][power]

    
def addVectors(vec1, vec2):
    res=[0,0,0,0,0,0,0,0]
    for i, (ele1, ele2) in enumerate(zip(vec1, vec2)):
        res[i] = ele1 ^ ele2
    return res

def mulVectors(vec, ele):
    res= [0,0,0,0,0,0,0,0]
    for i, e in enumerate(vec):
      res[i] = Mul(e,ele)
    return res
  
def LinearTransform(T_mat,elements):
    temp = [0,0,0,0,0,0,0,0]
    for vec,j in zip(T_mat,elements):
        temp = addVectors(mulVectors(vec,j),temp)
    return temp


# In[21]:


def EAEAE(pt,mat,exp_vec):
    plaintext = []
    
    for ch in pt:
        plaintext.append(ord(ch))
        
    text = [0 for i in range(8)]
    #E
    for i, e in enumerate(plaintext):
      text[i] = Exponent(e, exp_vec[i])
    #A
    text = LinearTransform(mat, text)
    #E
    for i, e in enumerate(text):
      text[i] = Exponent(e, exp_vec[i])
    #A
    text = LinearTransform(mat, text)
    #E
    for i, e in enumerate(text):
      text[i] = Exponent(e, exp_vec[i])
    return text


# In[22]:


def hex_rep(cipher_text):
    res = ""
    for i in range(0,len(cipher_text),2):
        chr1 = 16*(ord(cipher_text[i:i+2][0]) - ord('f'))
        chr2 = (ord(cipher_text[i:i+2][1]) - ord('f'))

        res = res+chr(chr1+chr2)
    return res


# In[23]:


def find_possible_values(plain,cipher):
    predicted_Diagonals_A = []
    for i in range(0,8):
        temp=[]
        for i in range(0,8):
            temp.append([])
        predicted_Diagonals_A.append(temp)

    predicted_exp = []
    for i in range(8):
        predicted_exp.append([])
    
    
    in_file = open(plain+".txt","r")
    out_file = open(cipher+".txt","r")
    i = 0
    for (inp_lines,out_lines) in zip(in_file.readlines(),out_file.readlines()):
        plaintexts = [hex_rep(t)[i] for t in inp_lines.strip().split(" ")]
        ciphertexts = [hex_rep(t)[i] for t in out_lines.strip().split(" ")]
        
        for k in range(1,127):
            for j in range(1,128):
                is_cand = True
                for inp,out in zip(plaintexts,ciphertexts):
                    p = ord(out)
                    c = Exponent(Mul(Exponent(Mul(Exponent(ord(inp), k), j), k), j), k)
                    if c != p:
                        is_cand = False
                if is_cand:
                    predicted_exp[i].append(k)
                    predicted_Diagonals_A[i][i].append(j)
        i += 1
    return predicted_exp,predicted_Diagonals_A


# In[24]:


predicted_EXP,predicted_diagonals = find_possible_values("plaintexts","ciphertexts")

print(predicted_diagonals)
print(predicted_EXP)


# In[25]:


def fun(i,ind):
    for p1, e1 in zip(predicted_EXP[ind+1], predicted_diagonals[ind+1][ind+1]):
          for p2, e2 in zip(predicted_EXP[ind], predicted_diagonals[ind][ind]):
              flag = True
              for inp, outp in zip(inpString, outString):
                  if(ord(outp) != Exponent(Mul(Exponent(Mul(Exponent(ord(inp), p2), e2), p2), i) ^Mul(Exponent(Mul(Exponent(ord(inp), p2), i), p1), e1), p1)):
                      flag = False
                      break
              if flag:
                  predicted_EXP[ind+1] = [p1]
                  predicted_diagonals[ind+1][ind+1] = [e1]
                  predicted_EXP[ind] = [p2]
                  predicted_diagonals[ind][ind] = [e2]
                  predicted_diagonals[ind][ind+1] = [i]

with open("plaintexts.txt", 'r') as input_file, open("ciphertexts.txt", 'r') as output_file:
  for ind, (iline, oline) in enumerate(zip(input_file.readlines(), output_file.readlines())):
      if ind > 6 :
          break

      inpString = [hex_rep(msg)[ind] for msg in iline.strip().split(" ")]
      outString = [hex_rep(msg)[ind+1] for msg in oline.strip().split(" ")]

      for i in range(1, 128):
              fun(i,ind)


# In[26]:


def find_transposed_matrix(p_diagonals):
    lin_trans = []
    lin_trans = [[0 for i in range(8)] for j in range(8)]
    for i in range(0,8):
        for j in range(0,8):
          if len(p_diagonals[i][j]) != 0:
            lin_trans[i][j] = p_diagonals[i][j][0]
          else:
            lin_trans[i][j] = 0
            
    return lin_trans


# In[27]:


def make_List_of_first(x):
    return [i[0] for i in x]


# In[28]:


def helper(i,index,offset,lin_trans_list):
      lin_trans_list[index][index+offset] = i
      flag = True
      for inps, outs in zip(input_string, output_string):
          if EAEAE(inps, lin_trans_list, exp_list)[index+offset] != ord(outs[index+offset]):
              flag = False
              break
      if flag==True:
          predicted_diagonals[index][index+offset] = [i]

for ofs in range(2,8):
    
    exp_list = make_List_of_first(predicted_EXP)
    
    lin_trans_mat = []
    for i in range(8):
        lin_trans_mat.append([0 for j in range(8)])
    
    
    for i in range(8):
      for j in range(8):     
        if(len(predicted_diagonals[i][j]) == 0):
          lin_trans_mat[i][j] = 0
        else:
          lin_trans_mat[i][j] = predicted_diagonals[i][j][0] 
    
    input_file = open("plaintexts.txt", 'r')
    output_file = open("ciphertexts.txt",'r')
    
    for index, (input,output) in enumerate(zip(input_file.readlines(),output_file.readlines())):
        if(index > (8-ofs-1)):
            continue
            
        input_string = [hex_rep(msg) for msg in input.strip().split(" ")]
        output_string = [hex_rep(msg) for msg in output.strip().split(" ")]
        for i in range(1,128):
            helper(i,index,ofs,lin_trans_mat)
    input_file.close()
    output_file.close()
    
lin_trans_list = [[0 for i in range(8)] for j in range(8)]
for i in range(0,8):
    for j in range(0,8):
      if len(predicted_diagonals[i][j]) == 0:
        lin_trans_list[i][j] = 0 
      else:
        lin_trans_list[i][j] = predicted_diagonals[i][j][0]


# In[29]:


def transpose(X):
    result = [[X[j][i] for j in range(len(X))] for i in range(len(X[0]))]
    return result


# In[30]:


print("The linear transmition matrix transpose is :")
print(lin_trans_list)
print("The linear transmition matrix is :")
print(transpose(lin_trans_list))
print("The Exponents vector is:")
print(exp_list)


# In[31]:


file = open("At_matrix.pkl", "wb")
pickle.dump(lin_trans_list, file)
file = open("Exp_vector.pkl", "wb")
pickle.dump(exp_list, file)


# In[32]:


file = open("Exp_vector.pkl", "wb")
pickle.dump(exp_list, file)

